'''Top-Level packages'''

__app_name__ = "mongocd"
__version__ = '0.0.1'

import logging
import multiprocess
from pymongo import MongoClient
from pythonjsonlogger import jsonlogger
from rich.logging import RichHandler
from logging import Logger

from kink import di
import typer
from mongocd.Domain.Base import *

from mongocd.Interfaces.Services import *
# from mongocd.Services import *
from mongocd.Services.VerifyService import VerifyService

# from mongocd.Domain.Database import *

cores: int = multiprocess.cpu_count()

#################logging##################
def init_logger() -> Logger:
    handler = logging.StreamHandler()  # Or FileHandler or anything else
    # Configure the fields to include in the JSON output. message is the main log string itself
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    logger = logging.getLogger(__name__)
    return logger

def validate_workingdir(config_folder_path: str,  logger: Logger) -> ReturnCodes | MongoMigration:
    '''Validate that working directory has the minimum capabilities
    for a successful weave.'''
    logger.info(Messages.dir_validation)

    if not os.path.exists(config_folder_path):
        logger.warning(f"{ReturnCodes.DIR_ACCESS_ERROR.name}: working {Messages.folder_inaccessible}: {config_folder_path}.")
        return ReturnCodes.DIR_ACCESS_ERROR

    #confirm that the folder has all the necessary files
    config_folder_contents = os.listdir(config_folder_path)
    for file_location in (FileStructure):
        full_path = f"{config_folder_path}{os.sep}{file_location.value}"
        if not os.path.exists(full_path):
            logger.warning(f"{ReturnCodes.UNINITIALIZED.name}: file missing from working dir: {full_path}. {Messages.run_init}")
            return ReturnCodes.UNINITIALIZED
    
    config_file_path = os.path.join(config_folder_path, FileStructure.CONFIGFILE.value)
    return config_file_path
    #ToDo check if files have been tampered with

    # with open(config_file_path, 'r') as file:
    #     yaml_data: dict = yaml.safe_load(file)
    #     migration_config_data = MongoMigration(**yaml_data)
    #     return migration_config_data
    
        
    
# mongoMigration: MongoMigration = MongoMigration()
# connectivityRetry = lambda x: mongoMigration.spec.connectivityRetry
# # secretVars: dict[str,str]
# destination_client: MongoClient = MongoClient()
# clients: dict[str, DbClients] = dict()

# c# like 🙂
def Main() -> None:
    logger = init_logger()
    di[Logger] = lambda x: logger
    CONFIG_FOLER_PATH = utils.get_full_path(
        os.getenv(Constants.config_folder_location_key, "MongoMigrate"))
    SOURCE_PASSWORD = os.getenv(Constants.mongo_source_pass)

    #need to deal with persisting SOURCE_PASSWORD
    if (CONFIG_FOLER_PATH is None or SOURCE_PASSWORD is None):
        logger.warning(f"""{ReturnCodes.UNINITIALIZED.name}: Required environment variables CONFIG_FOLER_PATH or SOURCE_PASSWORD is not set. {Messages.run_init}""")
    #Dependency Injection
    try:
        config_file_path = validate_workingdir(CONFIG_FOLER_PATH, di[Logger])

        #start out as null
        mongoMigration: MongoMigration = None
        clients: dict[str, DbClients] = None
        verifyService: IVerifyService = None
        
        #if validation was unsucessful
        if not isinstance(config_file_path, ReturnCodes):
            mongoMigration = MongoMigration().Init(config_file_path)

            for _databaseConfig in mongoMigration.spec.databaseConfig:
                required_args = [mongoMigration.spec.source_conn_string, SOURCE_PASSWORD, _databaseConfig.source_authdb,_databaseConfig.source_db]

                #if any of the required parameters to form the clients are not present then dont form the clients
                if None in required_args or '' in required_args:
                    continue
                clients[_databaseConfig.name] = DbClients(
                    source_conn_string=mongoMigration.spec.source_conn_string, source_password=SOURCE_PASSWORD, 
                    authSource=_databaseConfig.source_authdb, source_db=_databaseConfig.source_db)
                
            di[MongoMigration] = lambda x: mongoMigration
            di["clients"] = lambda x: clients
            di[IVerifyService] = lambda x: verifyService
            # print("ok")

    except OSError as ex:
        logger.error(f"{ReturnCodes.DIR_ACCESS_ERROR.name}: Error occurred while {Messages.dir_validation}")
        raise typer.Exit(ReturnCodes.DIR_ACCESS_ERROR.value)
    except Exception as ex:
        logger.fatal(f"{ReturnCodes.UNKNOWN_ERROR.name}: Unknown Error occurred while {Messages.dir_validation}")
        raise typer.Exit(ReturnCodes.UNKNOWN_ERROR.value)
    # di[IVerifyService] = VerifyService()

Main()