from dataclasses import dataclass
from enum import Enum
import logging
import os
from pydantic import BaseModel


class ReturnCode(Enum):
    SUCCESS = 0,
    ARG_ERROR = 1,
    DIR_ACCESS_ERROR = 2,
    READ_CONFIG_ERROR = 3,
    INVALID_CONFIG_ERROR = 4,
    EXTRACT_FILE_ERROR = 5,
    UNINITIALIZED = 6
    UNKNOWN_ERROR = 7
    ENVVAR_ACCESS_ERROR = 8
    DB_ACCESS_ERROR = 9,
    TIMEOUT_ERROR = 10,
    CONNECTION_ERROR = 11
    # error is reported from the db side
    DB_ERROR = 12
    EXECUTION_ERROR = 13
    VALIDATION_ERROR = 14
class Messages:
    run_init = """Please run mongocd init \
            or mongocd --help for usage details"""
    dir_validation = "Running working directory validations"
    write_file = "Writing file"
    extract_file = "Extracting file"
    remove_file = "Removing file"
    folder_inaccessible = "folder not found or inaccessible"
    envvar_inaccessible = "environment variable not found or inaccessible"
    specvalue_missing = "config spec value is missing or inaccessibe. Could it be a typo?"
    operation_timeout = "timeout while fetching resource or performing operation. make sure you're connected to the right public Network or VPN."
    empty_notallowed = "cannot be empty or null."


# ok = StarlarkContextClass()
# ok2 = ok.resource_list


class Constants(str, Enum):
    command = "command"
    document = "document"
    MONGOSOURCEPASSWORD = "i_have_no_password"
    CONFIGFOLDER = "MongoMigrate"
    sanitize_config = "SANITIZE_CONFIG"
    default_folder = 'MongoMigrate' # remove
    LOG_LEVEL = 'error'
    RENDER_ENV = ["dev"]
    db_name = 'db_name'
    coll_name = 'coll_name'
    source_collections = 'source_collections'
    source_collections_indices = 'source_collections_indices'
    unique_index_fields = 'unique_index_fields'
    source_data_json = 'source_data_json'
    unique_fields = 'unique_fields'
    rich_completed = '[green]◉[/green] Completed:'
    all = 'all'
    source = 'source'
    starlarkrun = 'StarlarkRun'
    configmap = 'ConfigMap'
    general_timeout = 15
    # js = '.js'

LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    Constants.LOG_LEVEL.value: logging.ERROR,
    "critical": logging.CRITICAL
}

class CustomResource(BaseModel):
    apiVersion: str = "migration.codejourney.io/v1alpha1"
    kind: str = "WeaveConfig"
    metadata: dict = dict()

class TemplatesFiles:
    getCollectionData = 'get-collection-data.js'
    utils = 'utils.js'
    copyIndices = 'copy-indices.js'
    compare_insert = 'compare-insert.js'
    duplicateCollections = 'duplicate-collections.js'
    copyData = 'copy-data.js'
    init_script = 'init_script.js'
    main_script = 'main.js'
    post_script = 'post_script.js'
    deleteDuplicateCollection = 'delete-duplicate-collection.js'
    starlarkrun = 'starlarkrun.star'

class FileStructure(Enum):

    def conform_path(input_path: str):
        """Ensure the path is os compliant"""
        converted_path = os.path.join(*input_path.split("\\"))
        return os.path.normpath(converted_path)
    
    CONFIGFILE = 'weaveconfig.yml'
    METAFOLDER = ".mongocd"
    JSTEMPLATESFOLDER = conform_path(f"{METAFOLDER}/jstemplates")
    GETCOLLECTIONDATA = conform_path(f'{JSTEMPLATESFOLDER}/{TemplatesFiles.getCollectionData}')
    UTILS = conform_path(f'{JSTEMPLATESFOLDER}/{TemplatesFiles.utils}')
    COPYINDICES = conform_path(f'{JSTEMPLATESFOLDER}/{TemplatesFiles.copyIndices}')
    DEEPCOMPARECOPY = conform_path(f'{JSTEMPLATESFOLDER}/{TemplatesFiles.compare_insert}')
    DUPLICATECOLLECTION = conform_path(f'{JSTEMPLATESFOLDER}/{TemplatesFiles.duplicateCollections}')
    COPYDATA = conform_path(f'{JSTEMPLATESFOLDER}/{TemplatesFiles.copyData}')
    # INIT_SCRIPT = conform_path(f'{JSTEMPLATESFOLDER}/init_script.js')
    DELETEDUPLICATECOLLECTION = conform_path(f'{JSTEMPLATESFOLDER}/{TemplatesFiles.deleteDuplicateCollection}')
    STARTEMPLATESFOLDER = conform_path(f"{METAFOLDER}/startemplates")
    OUTPUTFOLDER = "output"
    BASEFOLDER = "base"
    CHANGESETFOLDER = "changeset"
    OVERLAYSFOLDER = "overlays"
