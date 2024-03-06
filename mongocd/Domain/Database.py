import asyncio, aiofiles
from logging import Logger
import json, yaml, base64
from kink import inject
import os, re, tempfile
from typing import Self
from collections import defaultdict
from dataclasses import dataclass
from mongocd.Core import utils
from pydantic import BaseModel
from pymongo import MongoClient, database

from mongocd.Domain.Base import Constants, CustomResource, ReturnCodes


class CreateIndexOptions:
    ADD = "add"
    REPLACE = "replace"
    REMOVE = "remove"
    FALSE = "false"

class CollectionCommand(BaseModel):
    name: str = "*"
    command: str = "*"

class ShardData(BaseModel):
    database: bool = False #if database should be sharded
    commands: list[CollectionCommand] = list()

class CollectionProperty(BaseModel):
    name: str = ""
    # priority
    # 1. user defined unique_index_fields
    # 2. user defined unique_index_key
    # 3. default unique_index_fields set by default unique_index_key
    unique_index_key: str = "_id_"
    unique_index_fields: list[str] = list()
    #hidden from config
    indices: list[str] = list()
    excludeIndices: list[str] = list()
    includeIndices: list[str] = list()

    @inject
    def SetCollectionIndices(logger: Logger, self, db: database.Database) -> Self:
        if self.unique_index_key == None or len(self.unique_index_key) < 1:
            logger.warning(f"invalid value for unique_index_key: {self.unique_index_key}, using '_id_' instead")
            self.unique_index_key = "_id_"

        #else
        index_info = db[self.name].index_information()
        if (len(self.indices) > 0):
            self.indices = list(dict(index_info.items()).keys() & set(self.indices))
        else:
            self.indices = list(dict(index_info.items()).keys())

        for index, details in index_info.items():
            if index not in self.indices: #skip if doesnt match any index
                continue
            # if unique_index_fields have not been provided,
            # extract it from the unique_index_key
            if len(self.unique_index_fields) < 1 and index == self.unique_index_key:
                self.unique_index_fields = list(map(lambda key_info: key_info[0], details['key']))
                # print (self.unique_index_fields)
        # self.indices = [index['name'] for index in db[self.name].list_indexes()]
                
        self.indices = [index for index in self.indices
                    if not any([re.search(pattern, index)
                            for pattern in self.excludeIndices])]
            # collection_indices = set(collection_indices) - set(existing_property.excludeIndices)
        return self

class CollectionsConfig(BaseModel):
    excludeCollections: list[str] = list()
    includeCollections: list[str] = list()
    skipCollections: list[str] = list()
    properties: list[CollectionProperty] = list()

class DatabaseConfig(BaseModel):
    name: str = ""
    skip: bool = False
    # replicate_index: bool = False
    replicate_mode: str = Constants.command + Constants.document
    create_index: str | bool = True
    cleanup_backup: bool = True
    source_authdb: str = ""
    source_db: str = ""
    # destination_authdb: str
    destination_db: str = ""
    collections_config: CollectionsConfig = CollectionsConfig()
    shard: ShardData = ShardData()
    preCollectionCommands: str = "db.runCommand({ ping: 1 });"
    postCollectionCommands: str = "db.runCommand({ ping: 1 });"

    @inject
    def SetCollectionConfig(self, logger: Logger, db: database.Database) -> ReturnCodes:
        
        # exclude_filter = {'name': {'$not': {'$in': exclusion_list}}} #I wonder why I didnt use this
        # filter = {"name": {"$regex": r"^(?!system\.)"}}

        filter = {"name": {
            "$regex": r"^(?!system\.)",
            "$nin": self.collections_config.excludeCollections
            }
        }
        collection_names: list[str]
        try:
            collection_names = db.list_collection_names(filter=filter)
        except Exception as ex:
            logger.error("Unable to establish database session to fetch collection names")
            return ReturnCodes.DB_ACCESS_ERROR
        #if user specified includeCollections, then pick only the valid
        #collections out of what the user specified
        if (len(self.collections_config.includeCollections) > 0):
            collection_names = set(collection_names) & set(self.collections_config.includeCollections)

        #remove exclusion collections
        # exclusion_list = [r"^(?!system\.)"] #default
        # exclusion_list.extend(self.collections_config.excludeCollections)
        # exclusion_list = self.collections_config.excludeCollections
        # collection_names = [collection_name for collection_name in collection_names
        #                      if not any([re.search(pattern, collection_name) 
        #                         for pattern in exclusion_list])]

        existing_collection_properties = {prop.name: prop for prop in self.collections_config.properties}
        logger.info(f"database: {self.name} | collections: {collection_names}")

        # set collection properties
        for collection_name in collection_names:
            if collection_name in existing_collection_properties.keys():
                existing_collection_properties[collection_name].SetCollectionIndices(db)
                continue
            #create new collection property for each index
            self.collections_config.properties.append(
                CollectionProperty(name=collection_name).SetCollectionIndices(db))
        
        # _collectionConfig = self.collections_config
        #convert existing to dictionary
        # current_properties = {prop.name: prop for prop in self.collections_config.properties}
        #merge user defined properties and properties from database
        # new_properties = map(lambda collName: GetCollectionProperty
        #                      (db, collName, current_properties.get(collName)),collection_names)
        # self.collections_config.properties = list(new_properties)
        

        for property in self.collections_config.properties:
            logger.info(f"database: {self.name}, collection: {property.name}, excludeIndices: {property.excludeIndices}, unique_index_fields: {property.unique_index_fields}")
            logger.debug(f"database: {self.name}, indices: {property.indices}")
        return ReturnCodes.SUCCESS


class MongoMigrationSpec(BaseModel):
    secretVars: dict = dict()
    # dump_folder: str = "dump"
    source_conn_string: str = ""
    destination_conn_string: str = ""
    connectivityRetry: int = 5
    remote_template: str = "https://github.com/hayone1/MongoPrismSync/releases/download/v1alpha1_v0.0.1/templates_v1alpha1.zip"
    databaseConfig: list[DatabaseConfig] = [DatabaseConfig()]

class MongoMigration(CustomResource):
    spec: MongoMigrationSpec = MongoMigrationSpec()

    #if config is coming from file
    #didnt use __init__ because i'm not sure if safe_load will 
    #call __init__ again
    def Init(self: Self, config_file_path: str) -> Self:
        with open(config_file_path, 'r') as file:
            yaml_data: dict = yaml.safe_load(file)
            self = MongoMigration(**yaml_data)
            return self

@dataclass
class DbClients:
    pyclient: database.Database
    shclient: str
    shclientAsync: list[str]

    def __init__(self, source_conn_string: str, source_password: str, authSource: str, source_db):
        self.pyclient=MongoClient(source_conn_string, password=source_password, authSource=authSource)[source_db]
        self.shclient=f'mongosh "{source_conn_string}" --password {source_password} --authenticationDatabase {source_conn_string} --quiet --json=canonical'
        self.shclientAsync=['mongosh', source_conn_string, '--password', source_password, '--authenticationDatabase', source_conn_string, '--quiet', '--json=canonical']

    # def CreateClients(pyclientString: str, shclientString: str, shclientAsyncList: list[str]):
    #     pyclient

    def ShCommand (self, command: str):
        '''
        Runs command using mongosh installed on system
        remarks: quote commands using double quotes and any internal part
        of the command with single quotes
        '''
        # full_command = f' {" ".join(self.shclient)} --quiet --json=canonical --eval "{command}"'
        result = os.popen(f' {self.shclient} --eval "{command}"').read().rstrip()
        return json.loads(result)
    async def ShCommandAsync(self, command: str):
        '''
        Runs command asynchronously using mongosh installed on system
        remarks: quote commands using double quotes and any internal part
        of the command with single quotes
        '''
        full_command = self.shclientAsync + ['--eval', command]
        process = await asyncio.create_subprocess_exec(
            *full_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        # Wait for the process to complete
        stdout, stderr = await process.communicate()

        # Check the return code
        if process.returncode == 0:
            return json.loads(stdout.decode().rstrip())
        else:
            return stderr.decode().rstrip()
        # return json.loads(result)
    def ShFileCommand (self, command: str):
        with tempfile.NamedTemporaryFile(mode='w', delete=True) as tmpfl:
            tmpflName = tmpfl.name
            tmpfl.write(command)
            tmpfl.seek(0)
            query = f' {self.shclient} --eval "$(cat {tmpflName})"'
            result = os.popen(query).read().rstrip()
            return json.loads(result)
    async def ShFileCommandAsync (self, command: str):
        async with aiofiles.tempfile.NamedTemporaryFile(mode='w', delete=True) as tmpfl:
            tmpflName = tmpfl.name
            await tmpfl.write(command)
            await tmpfl.seek(0)

            full_command = self.shclient.split() + ['--eval', f"$(cat {tmpflName})"]
            process = await asyncio.create_subprocess_exec(
                *full_command,
                # f' {self.shclient} --quiet --json=canonical --eval "$(cat {tmpflName})"',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            # Wait for the process to complete
            stdout, stderr = await process.communicate()

            # Check the return code
            if process.returncode == 0:
                return json.loads(stdout.decode().rstrip())
            else:
                return stderr.decode().rstrip()
            # query = f' {self.shclient} --quiet --json=canonical --eval "$(cat {tmpflName})"'
            # result = os.popen(query).read().rstrip()
            # return json.loads(result)

# will this be memory hungry?
class DatabaseSyncScripts(BaseModel):
    # compiledScript: list[str] = list()
    databaseScript: list[str] = list()
    collectionScript: defaultdict[str, list[str]] = defaultdict(list)
    # databasePostScript: list[str] = list()
    # documentScript: list[str] = list() #unused
