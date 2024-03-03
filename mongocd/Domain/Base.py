from dataclasses import dataclass
from enum import Enum
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

class Constants:
    command = "command"
    document = "document"
    mongo_source_pass = "MONGOSOURCEPASSWORD"
    config_folder_location_key = "CONFIGFOLDER"
    sanitize_config = "SANITIZE_CONFIG"
    metafolder = ".mongocd"
    templatesfolder = ".mongocd/templates"

class CustomResource(BaseModel):
    apiVersion: str = "migration.codejourney.io/v1alpha1"
    kind: str = "PrismMigration"
    metadata: dict = dict()

class FileStructure(Enum):
    CONFIGFILE = 'prismconfig.yml'
    GETCOLLECTIONDATA = f'{Constants.templatesfolder}/get-data.js'
    FUNCTIONS = f'{Constants.templatesfolder}/functions.js'
    COPYINDICES = f'{Constants.templatesfolder}/copy-indices.js'
    DEEPCOMPARECOPY = f'{Constants.templatesfolder}/deep-compare-copy.js'
    DUPLICATECOLLECTION = f'{Constants.templatesfolder}/duplicate-collection.js'
    COPYDATA = f'{Constants.templatesfolder}/copy-data.js'
    BACKUP_SUFFIX = f'{Constants.templatesfolder}/_cd_backup'
    INIT_SCRIPT = f'{Constants.templatesfolder}/init_script.js'
    MAIN_SCRIPT = f'{Constants.templatesfolder}/main.js'
    POST_SCRIPT = f'{Constants.templatesfolder}/post_script.js'
    CLEANUPDUPLICATECOLLECTION = f'{Constants.templatesfolder}/delete-duplicate-collection.js'



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