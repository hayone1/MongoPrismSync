import os
from pathlib import Path
import typer
import yaml

from mongoprism import (
    SUCCESS, ARG_ERROR, DIR_ACCESS_ERROR, READ_CONFIG_ERROR, INVALID_CONFIG_ERROR
)
from mongoprism import logger
from mongoprism.core.domain import CustomResource, MongoMigration
from mongoprism.core import utils

config_file_name = "prismconfig.yaml"

def init_app(config_folder_path: str) -> int:
    '''Initialize the application'''
    # config_folder_path = Path(config_folder_dir)
    prismsync_config = _init_config_file(config_folder_path)
    #download templates

    #return error 
    if isinstance(prismsync_config, int): return prismsync_config

    utils.download_and_extract_zip(prismsync_config.spec.remote_template,
                                    config_folder_path + "/templates")

def _init_config_file(config_folder_path: str) -> int | MongoMigration:
    try:
        #Create folder
        config_folder = utils.get_full_path(config_folder_path)
        os.mkdirs(config_folder, exist_ok=True)
        #Create file
        config_file_path = os.path.join(config_folder, config_file_name)
        
        #get or initialize the config file
        migration_config_data = MongoMigration()
        if os.path.exists(config_file_path) and os.path.getsize(config_file_path) > 0:
            with open(config_file_path, 'r') as file:
                yaml_data: dict = yaml.safe_load(file)
                migration_config_data = MongoMigration(**yaml_data)
        else:
            #if file is empty or non existent, create a new file
            with open(config_file_path, 'w') as file:
                yaml.dump(vars(migration_config_data), file, default_flow_style=False)
        return migration_config_data
    except OSError as ex:
        logger.error(f"Error occurred while creating config_folder_path: {config_folder_path} | {ex}")
        return DIR_ACCESS_ERROR
    except Exception as ex:
        logger.error(f"Unknown Error occurred while creating or accessing config file: {config_folder_path} | {ex}")
        return DIR_ACCESS_ERROR
    # return SUCCESS
    