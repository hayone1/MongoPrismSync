import datetime
import os
from pathlib import Path
import traceback
import typer
import yaml

from mongoprism import (
    SUCCESS, ARG_ERROR, DIR_ACCESS_ERROR, READ_CONFIG_ERROR, INVALID_CONFIG_ERROR, EXTRACT_FILE_ERROR
)
from mongoprism import logger
from mongoprism.core.domain import CustomResource, MongoMigration, Constants
from mongoprism.core import utils

@staticmethod
def init_app(config_folder_path: str, source_password: str, sanitize_config: bool,
            init_template: bool = True,  template_url: str = None) -> int:
    '''Initialize the application defaults and files'''
    # config_folder_path = Path(config_folder_dir)
    prismsync_config = init_config_file(config_folder_path, sanitize_config, template_url)
    #download templates

    #return error 
    if isinstance(prismsync_config, int): return prismsync_config

    if init_template:
        extract_successful =  utils.download_and_extract_zip(prismsync_config.spec.remote_template,
                                    config_folder_path + "/templates")
        if extract_successful == False:
            return EXTRACT_FILE_ERROR
    os.environ[Constants.secret_vars_key] = source_password
    logger.info("Initialization Successful")
    return SUCCESS

@staticmethod
def init_config_file(config_folder_path: str, sanitize_config: bool = False, template_url: str = None) -> int | MongoMigration:
    '''Initialize configuration file'''
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
    # return SUCCESS

# init_config_file("MongoMigrate")


    