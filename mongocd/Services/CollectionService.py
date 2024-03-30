from logging import Logger
from typing import Any, Generator
from kink import inject
from jinja2 import Environment
from mongocd.Domain.MongoMigration import MongoMigration
from mongocd.Interfaces.Services import (
    ICollectionService, IPostRendererService
)
from mongocd.Domain.Database import *
from mongocd.Domain.Base import *
from accessify import implements, private
from rich.progress import Progress

@inject
@implements(ICollectionService)
class CollectionService():
    def __init__(self, templates: Environment, mongoMigration: MongoMigration,
            clients: dict[str, DbClients], post_render_service: IPostRendererService,
            logger: Logger = None,
            progress: Progress = None):
        self.logger = logger
        self.progress = progress
        self.templates = templates
        self.mongoMigration = mongoMigration
        self.clients = clients
        self.post_render_service = post_render_service

    async def form_documentsdata_async(self, databaseConfig: DatabaseConfig,
            collection_property: CollectionProperty, database_folder: str,
            top_level_commands: str) -> ReturnCode:
        #important! progress will only show if calling code is within a progress 'with' resource
        progress = self.progress
        # the database folder that contains the json data from the sourcedb unmodified
        # it is created in a location relative to the database_folder
        base_database_folder = utils.replace_nth_path_name(database_folder, -2, FileStructure.BASEFOLDER.value)
        changeset_folder = utils.replace_nth_path_name(database_folder, -2, FileStructure.CHANGESETFOLDER.value)

        #create collection folder
        overlay_collection_folder = f"{database_folder}/{collection_property.name}"
        base_collection_folder = f"{base_database_folder}/{collection_property.name}"
        changeset_collection_folder = f"{changeset_folder}/{collection_property.name}"
        os.makedirs(overlay_collection_folder, exist_ok=True)
        os.makedirs(base_collection_folder, exist_ok=True)
        os.makedirs(changeset_collection_folder, exist_ok=True)

        # with progress:
        # self.logger.debug(f"FormCollectionDataAsync Started: {databaseConfig.source_db} | {collection_property.name}")
        try:
            #get data from source collection
            fetch_sourcedata_task = progress.add_task(
                description=f"fetching data from source collection: {collection_property.name}",
                total=1
            )
            collection_documents_data = await self.download_documents_async(databaseConfig,
                    collection_property, [base_collection_folder, overlay_collection_folder])
            if isinstance(collection_documents_data, ReturnCode): return collection_documents_data

            utils.complete_richtask(
                fetch_sourcedata_task, 
                f"fetch data from source collection: {collection_property.name}"
            )

            #apply postrenders
            generate_changeset_task = progress.add_task(
                description=f"applying postrender for collection: {collection_property.name}",
                total=1
            )
            # for documents_data in collection_documents_data:

                #ToDo
                #apply changes to document and generate change final document changeset
                # documentFile = f'{collection_folder}/{documents_data.filename}.js'
                # if not os.path.exists(documentFile):


            utils.complete_richtask(
                generate_changeset_task, 
                f"apply postrender for collection: {collection_property.name}"
            )

            #generate script from template and write to file
            compare_insert_template = self.templates.get_template(TemplatesFiles.compare_insert)
            for documents_data in get_data_result:

                compare_insert_command = await compare_insert_template.render_async(
                    {
                        Constants.db_name.name: databaseConfig.destination_db,
                        Constants.coll_name.name: collection_property.name,
                        Constants.source_data_json.name: json.dumps(documents_data.value, indent=2),
                        Constants.unique_fields.name: json.dumps(documents_data.key, indent=2)
                    }
                )

                #write the generated document-level query to a file
                documentFile = f'{collection_folder}/{documents_data.filename}.js'
                with open(documentFile, 'w+') as document_file:
                    document_file.write(top_level_commands)
                    document_file.write(compare_insert_command)

            
            self.logger.debug(f"form_documentsdata_async Complete: {databaseConfig.source_db} | {collection_property.name}")
            return ReturnCode.SUCCESS
        except Exception as ex:
            self.logger.fatal(f"Unknown error occurred while weaving. {ex}")


    async def download_documents_async(self, databaseConfig: DatabaseConfig,
            collection_property: CollectionProperty,
            output_folders: list[str]) -> (ReturnCode | list[DocumentData]):
        get_collection_data_template = self.templates.get_template(TemplatesFiles.getCollectionData)
        get_collection_data_query = await get_collection_data_template.render_async(
            {
                Constants.db_name.name: databaseConfig.source_db,
                Constants.coll_name.name: collection_property.name,
                Constants.unique_index_fields.name: collection_property.unique_index_fields
            }
        )
        get_data_result: list[DocumentData] | ReturnCode = \
            await self.clients[databaseConfig.name].ShCommandAsync(get_collection_data_query, DocumentData)

        #if unsuccessful it will give a ReturnCode
        if isinstance(get_data_result, ReturnCode): return get_data_result
        
        #this will be the documents with ther database and collection info added to it
        # enriched_data = []
        for documents_data in get_data_result:
            for output_folder in output_folders:
                #write the fetched document to base folder
                document_filename = f'{output_folder}/{documents_data.filename}.json'
                with open(document_filename, 'w+') as document_file:
                    json.dump(documents_data.value, document_file, indent=2)
        return get_data_result
    


