
from logging import Logger
from kink import inject
from jinja2 import Environment
import typer
from mongocd.Domain.Base import FileStructure, TemplatesFiles
from mongocd.Domain.Database import *
from mongocd.Interfaces.Services import ICollectionService, IDatabaseService
from accessify import implements, private
from rich.progress import Progress

#inject is incompatible with implements
# @implements(IDatabaseService)
@inject
class DatabaseService(IDatabaseService):
    
    def __init__(self, templates: Environment, config_folder_path: str, 
                clients: dict[str, DbClients], databaseConfigs: list[DatabaseConfig],
                collection_service: ICollectionService, logger: Logger = None, progress: Progress = None):
            
            self.logger = logger
            self.progress = progress
            self.templates = templates
            self.clients = clients
            self.collection_service = collection_service
            self.output_folder = f"{config_folder_path}/{FileStructure.OUTPUTFOLDER.value}"
            self.databaseConfigs = databaseConfigs
            self.commandsList: DatabaseSyncScripts = DatabaseSyncScripts()


    @private
    async def generate_indexreplication_commandasync(self, databaseConfig: DatabaseConfig) -> str | ReturnCode:
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
            index_replication_command = await index_replication_template.render_async(
                {
                    Constants.db_name: databaseConfig.destination_db,
                    Constants.source_collections_indices: source_collection_indices
                }
            )
            return index_replication_command
        except Exception as ex:
            self.logger.error(f"Unknown error occured in generate_indexreplication_commandasync | {ex}")
            return ReturnCode.UNKNOWN_ERROR

    @private
    def generate_createcollection_command(self, db_name: str, collection_name: str) -> str:
        self.logger.info(f"adding create_collection_command for {collection_name}")
        create_collection_command = f"db.getSiblingDB('{db_name}').createCollection('{collection_name}');\n"
        return create_collection_command

    @private
    async def generate_duplicatecollection_commandasync(self, db_name, collections_config: CollectionsConfig) -> str:
        duplicate_collection_template = self.templates.get_template(TemplatesFiles.duplicateCollections)
        duplicate_collection_commands = await duplicate_collection_template.render_async(
            {
                Constants.db_name: db_name,
                Constants.source_collections: list(map(lambda prop: prop.name, collections_config.properties))
            }
        )
        return duplicate_collection_commands
    
    @private
    async def generate_deleteduplicatecollection_commandasync(self, db_name, collections_config: CollectionsConfig) -> str:
        delete_duplicate_collections_template = self.templates.get_template(TemplatesFiles.deleteDuplicateCollection)
        delete_duplicate_collections_commands = await delete_duplicate_collections_template.render_async(
            {
                Constants.db_name: db_name,
                Constants.source_collections: list(map(lambda prop: prop.name, collections_config.properties))
            }
        )
        return delete_duplicate_collections_commands
    
    async def generate_syncscripts_async(self) -> ReturnCode:
        logger = self.logger
        progress = self.progress
        commandsList = self.commandsList

        for databaseConfig in self.databaseConfigs:
            if databaseConfig.skip == True:
                logger.warning(f"DatabaseConfig [{databaseConfig.name}]: skip set to true, skipping...")
                continue

            #add utility functions and pre-collection commands to database script
            db_utils_commands = await self.templates.get_template(TemplatesFiles.utils).render_async()
            commandsList.databaseScript.append(db_utils_commands)
            commandsList.databaseScript.append(databaseConfig.preCollectionCommands)
            
            # add commands to create collections in the destination db if they dont exist
            for collection_property in databaseConfig.collections_config.properties:
                create_collection_command = self.generate_createcollection_command(databaseConfig.destination_db, collection_property.name)
                self.commandsList.databaseScript.append(create_collection_command)
                #add utility functions to all collection scripts
                commandsList.collectionScript[collection_property.name].append(db_utils_commands)

            #add command to replicate source collections indices to destination collections
            if (databaseConfig.create_index == True):
                replicate_indices_commands = await self.generate_indexreplication_commandasync(databaseConfig)
                #didnt want to usee a raise
                if isinstance(replicate_indices_commands, ReturnCode): typer.Exit(replicate_indices_commands.value)
                commandsList.databaseScript.append(replicate_indices_commands)

            # add commands to duplicate collections(+ their indices) in the destination db for backup purposes
            duplicate_collection_commands = await self.generate_duplicatecollection_commandasync(
                databaseConfig.destination_db, databaseConfig.collections_config)
            commandsList.databaseScript.append(duplicate_collection_commands)

            # add command to shard database. Generally This step needs to be done before any data is in the db
            # but would have no effect if db is already sharded
            if databaseConfig.shard.database == True:
                # first add enabe sharding command
                commandsList.databaseScript.append(f"db = db.getSiblingDB('{databaseConfig.destination_db}'); sh.enableSharding('{databaseConfig.destination_db}');\n")
                #then add user specified shard commands
                for shard_command in databaseConfig.shard.commands:
                    commandsList.databaseScript.append(shard_command.command)
                    # commandsList.compiledScript.append(shard_command.command)

            # remove the collection properties whose name matches the collection in the "skip" list
            # as they are not needed in the next steps
            collection_properties = [prop for prop in databaseConfig.collections_config.properties  
                            #pass the prop id no regex/item in the skip like matches it's name
                            if not any([re.search(pattern, prop.name)
                                    for pattern in databaseConfig.collections_config.skipCollections])]
            
            # create folder for database if it doesnt exist
            database_folder = f"{self.output_folder}{os.sep}{databaseConfig.name}"
            os.makedirs(database_folder, exist_ok=True)

            # using data from source db, add commands to add/update data in destination db's collection documents
            async with asyncio.TaskGroup() as tgrp:
                formDocumentsDataTasks = [
                    tgrp.create_task(
                        self.collection_service.form_documentsdata_async(databaseConfig, collection_property, database_folder)
                    ) for collection_property in collection_properties
                ]
            if any(tsk.result() != ReturnCode.SUCCESS for tsk in formDocumentsDataTasks):
                logger.error(f"Error occurred while fetching or generating data from sourcedb")

            #add post commands
            commandsList.databaseScript.append(databaseConfig.postCollectionCommands)


            # remove duplicate collections created. This is the last set of commands
            delete_duplicate_collections_commands = await self.generate_deleteduplicatecollection_commandasync(
                databaseConfig.destination_db, databaseConfig.collections_config)
            commandsList.databaseScript.append(delete_duplicate_collections_commands)

            # write database level commands
            database_file = f"{database_folder}/{TemplatesFiles.main_script}"
            with open(f'{database_file}', 'w+') as db_file:
                db_file.writelines(commandsList.databaseScript)
