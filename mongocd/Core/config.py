import os,traceback
from kink import inject
import yaml

from mongocd.Domain.Base import *
from mongocd.Domain.Database import MongoMigration
from mongocd.Core import utils
from mongocd.Interfaces.Services import *
from mongocd.Services.CollectionService import CollectionService
from mongocd.Services.DatabaseService import DatabaseService
from mongocd.Services.VerifyService import VerifyService



from pymongo import errors
from rich.logging import RichHandler
from logging import Logger
from kink import di
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
        SOURCE_PASSWORD = os.getenv(Constants.mongo_source_pass, "")
        if not utils.is_empty_or_whitespace(SOURCE_PASSWORD):
            #convert the password into asteric *
            record.msg = record.msg.replace(SOURCE_PASSWORD, ('*' * len(SOURCE_PASSWORD)))
        return True
    
#################logging##################
@staticmethod
def init_logger() -> Logger:
    #get log level from environment variable
    log_level_str = os.environ.get(Constants.log_level, Constants.default_log_level).lower()
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
    logger.info(f"{Messages.dir_validation}: {config_folder_path}")

    if not os.path.exists(config_folder_path):
        logger.warning(f"""{ReturnCode.DIR_ACCESS_ERROR.name}: working {Messages.folder_inaccessible}: {config_folder_path}.
                       Please set an accessible working folder with 'CONFIGFOLDER'
                       environment variable or with -o parameter. eg. mongocd weave -o 'folder'""")
        return ReturnCode.DIR_ACCESS_ERROR

    #confirm that the folder has all the necessary files
    # config_folder_contents = os.listdir(config_folder_path)
    for file_location in (FileStructure):
        full_path = f"{config_folder_path}{os.sep}{file_location.value}"
        if not os.path.exists(full_path):
            logger.warning(f"{ReturnCode.UNINITIALIZED.name}: file missing from working dir: {full_path}. {Messages.run_init}")
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
    logger = init_logger()
    di[Logger] = lambda x: logger

    CONFIG_FOLER_PATH = utils.get_full_path(
        os.getenv(Constants.config_folder_key, Constants.default_folder))
    SOURCE_PASSWORD = os.getenv(Constants.mongo_source_pass)

    #need to deal with persisting SOURCE_PASSWORD
    if (CONFIG_FOLER_PATH is None or SOURCE_PASSWORD is None):
        logger.warning(f"""{ReturnCode.UNINITIALIZED.name}: Required environment variables 
                       {Constants.config_folder_key} or {Constants.mongo_source_pass} is not set. {Messages.run_init}""")
    #Dependency Injection
    try:

        config_file_path = validate_workingdir(CONFIG_FOLER_PATH, di[Logger])

        #start out as null, dependencies need to be injected the order given
        mongoMigration: MongoMigration = None; di.factories[MongoMigration] = lambda x: mongoMigration
        clients: dict[str, DbClients] = None; di.factories["clients"] = lambda x: clients
        verifyService: IVerifyService = None; di.factories[IVerifyService] = lambda x: verifyService
        databaseService: IDatabaseService = None; di.factories[IDatabaseService] = lambda x: databaseService
        #if validation was sucessful, i.e it returned the config_file_path instead of a return code
        if isinstance(config_file_path, ReturnCode):
            return # dependencies will be None
        #else
        mongoMigration = MongoMigration().Init(config_file_path)
        clients = dict()
        for _databaseConfig in mongoMigration.spec.databaseConfig:
            required_args = [mongoMigration.spec.source_conn_string, SOURCE_PASSWORD, _databaseConfig.source_authdb,_databaseConfig.source_db]
            
            #if any of the required parameters to form the clients are not present 
            #then dont form the clients for this iteration
            if None in required_args or '' in required_args:
                continue
            #else
            clients[_databaseConfig.name] = DbClients(
                source_conn_string=mongoMigration.spec.source_conn_string, source_password=SOURCE_PASSWORD, 
                authSource=_databaseConfig.source_authdb, source_db=_databaseConfig.source_db, logger=logger)
        
        verifyService = VerifyService(mongoMigration, clients, logger)
        
        #no need to validate existence of folder as validate_workingdir would have done that
        template_abs_folder = f"{CONFIG_FOLER_PATH}{os.sep}{FileStructure.TEMPLATESFOLDER.value}"
        templates = Environment(loader=FileSystemLoader(template_abs_folder))

        collectionService = CollectionService(templates, mongoMigration, clients, logger)
        databaseService = DatabaseService(templates, config_file_path, clients, collectionService, logger)
            # print("ok")

    except OSError as ex:
        logger.fatal(f"{ReturnCode.DIR_ACCESS_ERROR.name}: Error occurred while {Messages.dir_validation}")
        return ReturnCode.DIR_ACCESS_ERROR
    except errors.ConfigurationError as ex:
        logger.error(f"{ReturnCode.TIMEOUT_ERROR}: {Messages.operation_timeout} | {ex}")
        return ReturnCode.TIMEOUT_ERROR.value
    except Exception as ex:
        logger.fatal(f"{ReturnCode.UNKNOWN_ERROR.name}: Unknown Error occurred while {Messages.dir_validation} | {ex}")
        return ReturnCode.UNKNOWN_ERROR.value
    
    return ReturnCode.SUCCESS
    # di[IVerifyService] = VerifyService()


@staticmethod
@inject
def init_configs(config_folder_path: str, sanitize_config: bool,
            update_templates: bool = True, template_url: str = None, logger: Logger = None) -> int:
    '''Initialize the application defaults and files'''
    # config_folder_path = Path(config_folder_dir)
    prismsync_config = init_config_file(config_folder_path, sanitize_config, template_url)
    #download templates

    #return error 
    if isinstance(prismsync_config, int): return prismsync_config
    template_abs_folder = f"{config_folder_path}{os.sep}{FileStructure.TEMPLATESFOLDER.value}"
    if update_templates:
        extract_successful = utils.download_and_extract_zip(prismsync_config.spec.remote_template,
                                template_abs_folder)
        if extract_successful == False:
            return ReturnCode.EXTRACT_FILE_ERROR
        
    #init output folder
    os.makedirs(f"{config_folder_path}/{FileStructure.OUTPUTFOLDER}", exist_ok=True)
    
    # os.environ[Constants.mongo_source_pass] = source_password
    logger.info("Initialization Successful")
    return ReturnCode.SUCCESS

@staticmethod
@inject
def init_config_file(config_folder_path: str, logger: Logger, sanitize_config: bool = False, template_url: str = None) -> int | MongoMigration:
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
        os.environ[Constants.config_folder_key] = config_folder
        return migration_config_data
    except OSError as ex:
        logger.error(f"{ReturnCode.DIR_ACCESS_ERROR.name}: Error occurred while {Messages.write_file}, {config_folder_path} | {ex}")
        return ReturnCode.DIR_ACCESS_ERROR
    except Exception as ex:
        logger.fatal(f"{ReturnCode.DIR_ACCESS_ERROR.name}: Unknown Error occurred while {Messages.write_file}, {config_folder_path} | {ex} | {traceback.format_exc()}")
        return ReturnCode.DIR_ACCESS_ERROR
    # return SUCCESS

    