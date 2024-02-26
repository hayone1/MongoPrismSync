import os
from pathlib import Path
import typer
import yaml

from mongoprism import (
    SUCCESS, ARG_ERROR, DIR_ACCESS_ERROR, READ_CONFIG_ERROR, INVALID_CONFIG_ERROR
)
from mongoprism import logger
from mongoprism.core.domain import MongoMigration

config_file_name = "prismconfig.yaml"

def init_app(config_folder_dir: str) -> int:
    '''Initialize the application'''
    # config_folder_path = Path(config_folder_dir)
    prismsync_config = _init_config_file(config_folder_dir)

def _init_config_file(config_folder_path: str) -> int:
    try:
        #Create folder
        current_directory = os.getcwd()
        config_folder = os.path.join(current_directory, config_folder_path)
        os.mkdirs(config_folder, exist_ok=True)
        #Create file
        config_file_path = os.path.join(config_folder, config_file_name)
        #if file is empty or non existent, create a new file
        if not os.path.exists(config_file_path) or os.path.getsize(config_file_path) == 0:
            with open(config_file_path, 'w') as file:
                yaml.dump(vars(MongoMigration()), file, default_flow_style=False)
        
    except OSError as ex:
        logger.error(f"Error occurred while creating config_folder_path: {config_folder_path} | {ex}")
        return DIR_ACCESS_ERROR
    return SUCCESS
    
def _init_templates(config_folder_path: str) -> int:
    
    