
from logging import Logger

from jinja2 import Environment
from mongocd.Domain.Base import FileStructure, TemplatesFiles
from mongocd.Domain.Database import *
from mongocd.Interfaces.Services import ICollectionService, IDatabaseService


class DatabaseService(IDatabaseService):
    def __init__(self, templates: Environment, config_folder_path: str, clients: dict[str, DbClients], collection_service: ICollectionService, logger: Logger):
            self.logger = logger
            self.templates = templates
            self.clients = clients
            self.collection_service = collection_service
            self.output_folder = f"{config_folder_path}/{FileStructure.OUTPUTFOLDER}"

    async def GenerateIndexReplicationCommandAsync(self, databaseConfig: DatabaseConfig) -> str | ReturnCode:
        '''Pulls index data from collections of source db and returns mongosh commands that can be 
        used to reproduce them in the destination db.

        Returns ReturnCode.UNKNOWN_ERROR if error occurs.
        '''
        self.logger.info(f"GenerateIndexCreationCommandAsync Started: {databaseConfig.source_db}")
        try:
            async with asyncio.TaskGroup() as tgrp:
                #get index details for each collection
                get_indices_tasks = [
                    tgrp.create_task(
                        self.clients[databaseConfig.name].ShCommandAsync(
                                f'printjson({{"collName": "{collection_property.name}",\
                                    "indices": db.getSiblingDB("{databaseConfig.source_db}")["{collection_property.name}"]\
                                        .getIndexes()}});'
                        )
                    )for collection_property in databaseConfig.collections_config.properties
                ]
                source_collection_indices = [tsk.result() for tsk in get_indices_tasks]
                
            index_replication_template = self.templates.get_template(TemplatesFiles.copyIndices)
            index_replication_command = index_replication_template.render(
                {
                    Constants.db_name: databaseConfig.destination_db,
                    Constants.source_collections_indices: source_collection_indices
                }
            )
            return index_replication_command
        except Exception as ex:
            self.logger.error(f"Unknown error occured in GenerateIndexReplicationCommandAsync | {ex}")
            return ReturnCode.UNKNOWN_ERROR

    async def GenerateSyncScriptsAsync(self, databaseConfig: DatabaseConfig):
        logger = self.logger
        if databaseConfig.skip == True:
            logger.warning(f"DatabaseConfig [{databaseConfig.name}]: skip set to true, skipping...")
            return
        
        commandsList: DatabaseSyncScripts = DatabaseSyncScripts()

        #add utility functions and pre-collection commands
        db_utils_commands = self.templates.get_template(TemplatesFiles.utils).render()
        commandsList.databaseScript.append(db_utils_commands)
        commandsList.databaseScript.append(databaseConfig.preCollectionCommands)
        
        # add commands to create collections in the destination db if they dont exist
        for collection_property in databaseConfig.collections_config.properties:
            logger.info(f"adding create_collection_command for {collection_property.name}")
            create_collection_command = f"db.getSiblingDB('{databaseConfig.destination_db}').createCollection('{collection_property.name}');\n"
            commandsList.databaseScript.append(create_collection_command)
            #add utility functions to collections script
            commandsList.collectionScript[collection_property.name].append(db_utils_commands)

        duplicate_collection_template = self.templates.get_template(TemplatesFiles.duplicateCollections)
        duplicate_collection_command = duplicate_collection_template.render(
            {
                Constants.db_name: databaseConfig.destination_db,
                Constants.source_collections: databaseConfig.collections_config.properties
            }
        )
        commandsList.databaseScript.append(duplicate_collection_command)

        # add command to shard database. Generally This step needs to be done before any data is in the db
        # but would have no effect if db is already sharded
        if databaseConfig.shard.database == True:
            # first add enabe sharding command
            commandsList.databaseScript.append(f"db = db.getSiblingDB('{databaseConfig.destination_db}'); sh.enableSharding('{databaseConfig.destination_db}');\n")
            for shard_command in databaseConfig.shard.commands:
                commandsList.databaseScript.append(shard_command.command)
                # commandsList.compiledScript.append(shard_command.command)

        #add command to replicate collection indices to destination db collections
        if (databaseConfig.create_index == True):
            replicate_indices_commands = await self.GenerateIndexReplicationCommandAsync(databaseConfig)
            commandsList.databaseScript.append(replicate_indices_commands)

        #remove the collection properties whose name matches the collection in the skip list
        #as they are not needed in the next steps
        collection_properties = [prop for prop in databaseConfig.collections_config.properties  
                        #pass the prop id no regex/item in the skip like matches it's name
                        if not any([re.search(pattern, prop.name)
                                for pattern in databaseConfig.collections_config.skipCollections])]
        

        database_folder = f"{self.output_folder}{os.sep}{databaseConfig.name}"
        os.makedirs(database_folder, exist_ok=True)

        # using data from source db, add commands to add/update data in destination db's collection documents
        async with asyncio.TaskGroup() as tgrp:
            formDocumentsDataTasks = [
                tgrp.create_task(
                    self.collection_service.FormDocumentsDataAsync(databaseConfig, collection_property, database_folder)
                ) for collection_property in collection_properties
            ]

        #run commands after working with collections
        commandsList.databaseScript.append(databaseConfig.postCollectionCommands)
        # commandsList.compiledScript.append(databaseConfig.postCollectionCommands)


        # remove duplicate collections created. This is the last set of commands
        delete_duplicate_collections_template = self.templates.get_template(FileStructure.DELETEDUPLICATECOLLECTION)
        delete_duplicate_collections_command = await delete_duplicate_collections_template.render_async(
            {
                Constants.db_name: databaseConfig.destination_db,
                Constants.source_collections: databaseConfig.collections_config.properties
            }
        )
        commandsList.databaseScript.append(delete_duplicate_collections_command)

        # if Constants.command not in databaseConfig.replicate_mode:
        #     return
        # write compiled commands 
        
        # write database level commands
        database_file = f"{database_folder}/{TemplatesFiles.main_script}"
        with open(f'{database_file}', 'w+') as db_file:
            db_file.writelines(commandsList.databaseScript)
