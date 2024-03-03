from dataclasses import dataclass
from enum import Enum
import os
from typing import Self
from pydantic import BaseModel

class ReturnCodes(Enum):
    SUCCESS = 0,
    ARG_ERROR = 1,
    DIR_ACCESS_ERROR = 2,
    READ_CONFIG_ERROR = 3,
    INVALID_CONFIG_ERROR = 4,
    EXTRACT_FILE_ERROR = 5,
    UNINITIALIZED = 6
    UNKNOWN_ERROR = 7

class Messages:
    run_init = f"""Please run mongocd init
            or mongocd --help for usage details"""
    dir_validation = "Running working directory validations"
    write_file = "Writing file"
    extract_file = "Extracting file"
    remove_file = "Removing file"
    folder_inaccessible = "folder not found or inaccessible"

class Constants:
    command = "command"
    document = "document"
    mongo_source_pass = "MONGOSOURCEPASSWORD"
    config_folder_location_key = "CONFIGFOLDER"
    sanitize_config = "SANITIZE_CONFIG"
    backup_suffix = "_cd_backup"
    main_script = 'main.js'
    post_script = 'post_script.js'

class CustomResource(BaseModel):
    apiVersion: str = "migration.codejourney.io/v1alpha1"
    kind: str = "PrismMigration"
    metadata: dict = dict()

class FileStructure(Enum):

    def conform_path(input_path: str):
        '''Ensure the path is os compliant'''
        converted_path = os.path.join(*input_path.split("\\"))
        return os.path.normpath(converted_path)
    
    METAFOLDER = ".mongocd"
    TEMPLATESFOLDER = conform_path(f"{METAFOLDER}/templates")
    CONFIGFILE = 'prismconfig.yml'
    GETCOLLECTIONDATA = conform_path(f'{TEMPLATESFOLDER}/get-data.js')
    FUNCTIONS = conform_path(f'{TEMPLATESFOLDER}/functions.js')
    COPYINDICES = conform_path(f'{TEMPLATESFOLDER}/copy-indices.js')
    DEEPCOMPARECOPY = conform_path(f'{TEMPLATESFOLDER}/deep-compare-copy.js')
    DUPLICATECOLLECTION = conform_path(f'{TEMPLATESFOLDER}/duplicate-collection.js')
    COPYDATA = conform_path(f'{TEMPLATESFOLDER}/copy-data.js')
    # INIT_SCRIPT = conform_path(f'{TEMPLATESFOLDER}/init_script.js')
    CLEANUPDUPLICATECOLLECTION = conform_path(f'{TEMPLATESFOLDER}/delete-duplicate-collection.js')




class TemplatesFiles:
    getCollectionData = 'get-data.js'
    functions = 'functions.js'
    copyIndices = 'copy-indices.js'
    deepCompareCopy = 'deep-compare-copy.js'
    duplicateCollection = 'duplicate-collection.js'
    copyData = 'copy-data.js'
    backup_suffix = '_cd_backup'
    init_script = 'init_script.js'
    main_script = 'main.js'
    post_script = 'post_script.js'
    cleanupDuplicateCollection = 'delete-duplicate-collection.js'