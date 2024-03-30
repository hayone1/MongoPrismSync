import os
import traceback
from kink import inject, di
from pydantic_core import ValidationError
import starlark_go
import yaml

from mongocd.Domain.Base import *
from mongocd.Domain.MongoMigration import MongoMigration
from mongocd.Core import utils
from mongocd.Interfaces.Services import *
from mongocd.Services.CollectionService import CollectionService
from mongocd.Services.DatabaseService import DatabaseService
from mongocd.Services.VerifyService import VerifyService

import logging
from rich import print
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from logging import Logger

from pymongo import errors
from jinja2 import Environment, FileSystemLoader
# from mongocd.Domain.Database import *

cores: int = os.cpu_count()
__app_name__ = "mongocd"
__version__ = '0.0.1'

class PasswordFilter(logging.Filter):
    # def __init__(self):
    #     logging.Filter.__init__(self)

    def filter(self, record: logging.LogRecord) -> bool:
        # Replace 'password' with a placeholder in the log message
        SOURCE_PASSWORD = os.getenv(Constants.MONGOSOURCEPASSWORD.name, "")
        if not utils.is_empty_or_whitespace(SOURCE_PASSWORD):
            #convert the password into asteric *
            record.msg = record.msg.replace(SOURCE_PASSWORD, ('*' * len(SOURCE_PASSWORD)))
        return True
    
#################logging##################
@staticmethod
def init_logger() -> Logger:
    #get log level from environment variable
    log_level_str = os.environ.get(Constants.LOG_LEVEL.name, Constants.LOG_LEVEL.value).lower()
    log_level = LOG_LEVEL_MAP.get(log_level_str)

    handler = logging.StreamHandler()  # Or FileHandler or anything else
    # Configure the fields to include in the JSON output. message is the main log string itself
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    logger = logging.getLogger(__name__)
    logger.addFilter(PasswordFilter())
    return logger
@staticmethod
def validate_workingdir(config_folder_path: str,  logger: Logger) -> ReturnCode | MongoMigration:
    '''Validate that working directory has the minimum capabilities
    for a successful weave.'''
    logger.debug(f"{Messages.dir_validation}: {config_folder_path}")

    if not os.path.exists(config_folder_path):
        logger.warning(
        f"""{ReturnCode.DIR_ACCESS_ERROR.name}: default working {Messages.folder_inaccessible}: {config_folder_path}.
            Ignore this warning if working folder already set with 'CONFIGFOLDER' environment variable 
            or with -o parameter. eg. mongocd weave -o 'folder'""")
        return ReturnCode.DIR_ACCESS_ERROR

    #confirm that the folder has all the necessary files
    # config_folder_contents = os.listdir(config_folder_path)
    for directory in (FileStructure):
        full_path = f"{config_folder_path}{os.sep}{directory.value}"
        if not os.path.exists(full_path):
            #This does not seem to work on folder
            logger.warning(f"{ReturnCode.UNINITIALIZED.name}: file or folder missing from working dir: {full_path}. {Messages.run_init}")
            return ReturnCode.UNINITIALIZED
    
    config_file_path = os.path.join(config_folder_path, FileStructure.CONFIGFILE.value)
    return config_file_path
    #ToDo check if files have been tampered with

    # with open(config_file_path, 'r') as file:
    #     yaml_data: dict = yaml.safe_load(file)
    #     migration_config_data = MongoMigration(**yaml_data)
    #     return migration_config_data
    
@staticmethod
def inject_dependencies() -> ReturnCode:
    """
    instantiate dependencies needed for app
    """
    
    if Logger not in di:
        di[Logger] = init_logger()

    if Progress not in di:
        di[Progress] = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"), 
            transient=False
        )
    logger = di[Logger]
    progress = di[Progress]
    starlark_go.configure_starlark(allow_set=True)

    CONFIG_FOLER_PATH = utils.get_full_path(
        os.getenv(Constants.CONFIGFOLDER.name, Constants.CONFIGFOLDER.value))
    SOURCE_PASSWORD = os.getenv(Constants.MONGOSOURCEPASSWORD.name)

    #need to deal with persisting SOURCE_PASSWORD
    if (CONFIG_FOLER_PATH is None or SOURCE_PASSWORD is None):
        logger.warning(f"""{ReturnCode.UNINITIALIZED.name}: Required environment variables 
                       {Constants.CONFIGFOLDER.name} or {Constants.MONGOSOURCEPASSWORD.name} is not set. {Messages.run_init}""")
    try:
        with progress:
            config_file_path = validate_workingdir(CONFIG_FOLER_PATH, di[Logger])

        #start out as null, dependencies need to be injected the order given
        di['config_folder_path'] = CONFIG_FOLER_PATH
        di[MongoMigration] = None
        di["clients"] = None
        di[IVerifyService] = None
        di[IDatabaseService] = None
        #if validation was sucessful, i.e it returned the config_file_path instead of a return code
        if isinstance(config_file_path, ReturnCode):
            return # dependencies will be None
        #else
        # mongoMigration = MongoMigration().Init(config_file_path)
        with open(config_file_path, 'r') as file:
            yaml_data: dict = yaml.safe_load(file)
            di[MongoMigration] = MongoMigration(**yaml_data)

        di["clients"] = dict()
        for databaseConfig in di[MongoMigration].spec.databaseConfigs:
            required_args = [di[MongoMigration].spec.source_conn_string, SOURCE_PASSWORD,
                            databaseConfig.source_authdb,databaseConfig.source_db]
            
            #if any of the required parameters to form the clients are not present 
            #then dont form the clients for this iteration
            if None in required_args or '' in required_args:
                continue
            #else
            di["clients"][databaseConfig.name] = DbClients(
                source_conn_string=di[MongoMigration].spec.source_conn_string, source_password=SOURCE_PASSWORD, 
                authSource=databaseConfig.source_authdb, source_db=databaseConfig.source_db)
        
        di[IVerifyService] = VerifyService(di[MongoMigration], di["clients"])
        
        #no need to validate existence of folder as validate_workingdir would have done that
        template_abs_folder = f"{CONFIG_FOLER_PATH}{os.sep}{FileStructure.JSTEMPLATESFOLDER.value}"
        templates = Environment(loader=FileSystemLoader(template_abs_folder), enable_async=True)

        collectionService = CollectionService(templates, di[MongoMigration], di["clients"])
        di[IDatabaseService] = DatabaseService(templates, CONFIG_FOLER_PATH, di["clients"],
                                          di[MongoMigration].spec.databaseConfigs, collectionService)
            # print("ok")

    except OSError as ex:
        logger.fatal(f"{ReturnCode.DIR_ACCESS_ERROR.name}: Error occurred while {Messages.dir_validation}")
        return ReturnCode.DIR_ACCESS_ERROR
    except errors.ConfigurationError as ex:
        logger.error(f"{ReturnCode.TIMEOUT_ERROR}: {Messages.operation_timeout} | {ex}")
        return ReturnCode.TIMEOUT_ERROR
    except ValidationError as ex:
        logger.error(f"{ReturnCode.INVALID_CONFIG_ERROR}: Please check weaveconfig.yml for correctness | {ex}")
        return ReturnCode.INVALID_CONFIG_ERROR
    except Exception as ex:
        logger.fatal(f"{ReturnCode.UNKNOWN_ERROR.name}: Unknown Error occurred while {Messages.dir_validation} | {ex} | {ex.__class__}")
        return ReturnCode.UNKNOWN_ERROR
    
    return ReturnCode.SUCCESS
    # di[IVerifyService] = VerifyService()

# @staticmethod
# @inject
# def refresh_dependencies() -> ReturnCode:
    # skip logger
    # skip progress



@staticmethod
@inject
def init_configs(config_folder_path: str, sanitize_config: bool,
            update_templates: bool = True, template_url: str = None,
            logger: Logger = None, progress: Progress = None) -> ReturnCode:
    '''Initialize the application defaults and files'''
    # config_folder_path = Path(config_folder_dir)
    # progress is already injected but needs "with" to work
    # with progress:
    init_file_task = progress.add_task(description="initializing config file...", total=None)
    prismsync_config = init_config_file(config_folder_path, sanitize_config, template_url)
    #return error 
    if isinstance(prismsync_config, ReturnCode): return prismsync_config
    # progress.update(init_file_task, completed=True)
    # progress.update(init_file_task, advance=1,completed=True)
    utils.complete_richtask(init_file_task, "configfile initialization successful")

    #download templates
    template_abs_folder = f"{config_folder_path}{os.sep}{FileStructure.JSTEMPLATESFOLDER.value}"
    if update_templates:
        # with progress:
        zip_task = progress.add_task(description="updating templates...", total=None)
        extract_status = utils.download_and_extract_zip(prismsync_config.spec.remote_template,
                                template_abs_folder)
        if extract_status != ReturnCode.SUCCESS:
            return extract_status
        utils.complete_richtask(zip_task, "template update successful")
    
    #init folders
    for directory in (FileStructure):
        # skip if it is a file
        if os.path.splitext(directory.value)[1]: continue
        try:
            full_path = f"{config_folder_path}{os.sep}{directory.value}"
            os.makedirs(full_path, exist_ok=True)  # Create folder, ignore if exists
        except OSError as ex:
            print(f"Error creating folder {full_path}: {ex}")
            return ReturnCode.DIR_ACCESS_ERROR
    # os.makedirs(f"{config_folder_path}/{FileStructure.OUTPUTFOLDER.value}", exist_ok=True)
    # os.makedirs(f"{config_folder_path}/{FileStructure.BASEFOLDER.value}", exist_ok=True)
    # os.makedirs(f"{config_folder_path}/{FileStructure.CHANGESETFOLDER.value}", exist_ok=True)
    
    # os.environ[Constants.mongo_source_pass] = source_password
    print("[green]Initialization Successful")
    return ReturnCode.SUCCESS

@staticmethod
@inject
def init_config_file(config_folder_path: str, sanitize_config: bool = False,
                    template_url: str = None, logger: Logger =  None
                    ) -> ReturnCode | MongoMigration:
    '''Initialize configuration file'''
    # print("Init config file called")
    # print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        #Create folder
        config_folder = utils.get_full_path(config_folder_path)
        os.makedirs(config_folder, exist_ok=True)
        #get file path
        config_file_path = os.path.join(config_folder, FileStructure.CONFIGFILE.value)
        
        #get or initialize the config file
        migration_config_data = MongoMigration()
        migration_config_data.spec.remote_template = (template_url if template_url != None
                    else migration_config_data.spec.remote_template)
        #If the config file already exists
        if os.path.exists(config_file_path) and os.path.getsize(config_file_path) > 0:
            with open(config_file_path, 'r') as file:
                yaml_data: dict = yaml.safe_load(file)
                migration_config_data = MongoMigration(**yaml_data)
            if sanitize_config:
                migration_config_data.spec.remote_template = (template_url if template_url != None
                    else migration_config_data.spec.remote_template)
                with open(config_file_path, 'w') as file:
                    yaml.dump(migration_config_data.model_dump(), file, default_flow_style=False)
        else:
            # print("Init config file called: Write")
            #if file is empty or non existent, create a new file
            with open(config_file_path, 'w') as file:
                yaml.dump(migration_config_data.model_dump(), file, default_flow_style=False)
        os.environ[Constants.CONFIGFOLDER.name] = config_folder
        return migration_config_data
    except OSError as ex:
        logger.fatal(f"{ReturnCode.DIR_ACCESS_ERROR.name}: Error occurred while {Messages.write_file}, {config_folder_path} | {ex}")
        return ReturnCode.DIR_ACCESS_ERROR
    except ValidationError as ex:
        logger.fatal(f"{ReturnCode.INVALID_CONFIG_ERROR}: Please check weaveconfig.yml for correctness | {ex}")
        return ReturnCode.INVALID_CONFIG_ERROR
    except Exception as ex:
        logger.fatal(f"{ReturnCode.DIR_ACCESS_ERROR.name}: Unknown Error occurred while {Messages.write_file}, {config_folder_path} | {ex} | {traceback.format_exc()}")
        return ReturnCode.DIR_ACCESS_ERROR
    # return SUCCESS

    