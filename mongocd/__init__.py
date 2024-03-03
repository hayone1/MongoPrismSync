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

def validate_workingdir(config_folder_path: str, source_password: str,  logger: Logger) -> ReturnCodes | MongoMigration:
    '''Validate that working directory has the minimum capabilities
    for a successful weave.'''
    logger.info(Messages.dir_validation)
    if (config_folder_path is None or source_password is None):
        logger.warning(f"""{ReturnCodes.UNINITIALIZED.name}: Required Parameters not initialized. {Messages.run_init}""")
        return ReturnCodes.UNINITIALIZED
    
    #confirm that the folder has all the necessary files
    config_folder_contents = os.listdir(config_folder_path)
    for file_location in (FileStructure):
        if not os.path.exists(f"{config_folder_path}/{file_location.value}"):
            logger.warning(f"{ReturnCodes.UNINITIALIZED.name}: file missing from working dir: {file_location.value}. {Messages.run_init}")
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
    CONFIG_FOLER_PATH = os.getenv(Constants.config_folder_location_key)
    SOURCE_PASSWORD = os.getenv(Constants.mongo_source_pass)

    #Dependency Injection
    try:
        config_file_path = validate_workingdir(CONFIG_FOLER_PATH, SOURCE_PASSWORD, logger)
        #if validation was unsucessful
        if isinstance(config_file_path, ReturnCodes):
            di[MongoMigration] = None
            di["clients"] = None
            di[IVerifyService] = None
        else:
        
            mongoMigration = MongoMigration().Init(config_file_path)

            clients: dict[str, DbClients] = dict()
            for _databaseConfig in mongoMigration.spec.databaseConfig:
                clients[_databaseConfig.name] = DbClients(
                    mongoMigration.spec.source_conn_string, password=SOURCE_PASSWORD, 
                    authSource=_databaseConfig.source_authdb, source_db=_databaseConfig.source_db)
                
            di[MongoMigration] = lambda x: mongoMigration
            di["clients"] = lambda x: clients

            di[IVerifyService] = VerifyService()
            # print("ok")

    except OSError as ex:
        logger.error(f"{ReturnCodes.DIR_ACCESS_ERROR.name}: Error occurred while {Messages.dir_validation}")
        raise typer.Exit(ReturnCodes.DIR_ACCESS_ERROR.value)
    except Exception as ex:
        logger.fatal(f"{ReturnCodes.UNKNOWN_ERROR.name}: Unknown Error occurred while {Messages.dir_validation}")
        raise typer.Exit(ReturnCodes.UNKNOWN_ERROR.value)
    # di[IVerifyService] = VerifyService()

Main()