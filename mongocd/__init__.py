'''Top-Level packages'''

__app_name__ = "mongoprism"
__version__ = '0.0.1'

import logging
import multiprocess
from pymongo import MongoClient
from pythonjsonlogger import jsonlogger
from rich.logging import RichHandler
from logging import Logger

from kink import di
from distutils.util import strtobool

from mongocd.Services.Interfaces import *
from mongocd.Services import *

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

def init_config_file(config_folder_path: str, sanitize_config: bool = False, template_url: str = None) -> int | MongoMigration:
    '''Initialize configuration file'''
    CONFIG_FOLDER_PATH = os.getenv(Constants.config_folder_location_key, "MongoMigrate")
    SOURCE_PASSWORD = os.getenv(Constants.mongo_source_pass, "MongoMigrate")
    SANITIZE_CONFIG = bool(strtobool(os.getenv(Constants.sanitize_config, "true")))
    # argParser.add_argument("-t", "--testMode", type=lambda x: bool(strtobool(x)), help=f'When set to true, generated manifests will be saved into output folder and not applied to cluster. Default: fa;se')

    # print("Init config file called")
    # print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        #Create folder
        config_folder = utils.get_full_path(config_folder_path)
        os.makedirs(config_folder, exist_ok=True)
        #Create file
        config_file_path = os.path.join(config_folder, Constants.config_file_name)
        
        #get or initialize the config file
        migration_config_data = MongoMigration()
        migration_config_data.spec.remote_template = (template_url if template_url != None
                    else migration_config_data.spec.remote_template)
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
            print("Init config file called: Write")
            #if file is empty or non existent, create a new file
            with open(config_file_path, 'w') as file:
                yaml.dump(migration_config_data.model_dump(), file, default_flow_style=False)
        os.environ[Constants.config_folder_location_key] = config_folder
        return migration_config_data
    except OSError as ex:
        logger.error(f"Error occurred while creating config_folder_path: {config_folder_path} | {ex}")
        return DIR_ACCESS_ERROR
    except Exception as ex:
        logger.fatal(f"Unknown Error occurred while creating or accessing config file: {config_folder_path} | {ex} | {traceback.format_exc()}")
        return DIR_ACCESS_ERROR
    
# mongoMigration: MongoMigration = MongoMigration()
# connectivityRetry = lambda x: mongoMigration.spec.connectivityRetry
# # secretVars: dict[str,str]
# destination_client: MongoClient = MongoClient()
# clients: dict[str, DbClients] = dict()

def bootstrap_di() -> None:
    logger = init_logger()
    di[Logger] = lambda x: logger
    di[IVerifyService] = VerifyService()