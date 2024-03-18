from logging import Logger
from kink import inject
from jinja2 import Environment
from mongocd.Interfaces.Services import ICollectionService
from mongocd.Domain.Database import *
from mongocd.Domain.Base import *
from accessify import implements
from rich.progress import Progress

@inject
@implements(ICollectionService)
class CollectionService():
    def __init__(self, templates: Environment, mongoMigration: MongoMigration,
                clients: dict[str, DbClients], logger: Logger = None, progress: Progress = None):
            self.logger = logger
            self.progress = progress
            self.templates = templates
            self.mongoMigration = mongoMigration
            self.clients = clients

    async def form_documentsdata_async(self, databaseConfig: DatabaseConfig,
            collection_property: CollectionProperty, database_folder: str) -> ReturnCode:
        #important! progress will only show if calling code is within a progress 'with' resource
        progress = self.progress
        # with progress:
        # self.logger.debug(f"FormCollectionDataAsync Started: {databaseConfig.source_db} | {collection_property.name}")
        try:
            collection_weave_task = progress.add_task(
                description=f"building weave queries for collection: {collection_property.name}",
                total=1
            )
            #get data from source collection
            get_collection_data_template = self.templates.get_template(TemplatesFiles.getCollectionData)
            get_collection_data_query = await get_collection_data_template.render_async(
                {
                    Constants.db_name: databaseConfig.source_db,
                    Constants.coll_name: collection_property.name,
                    Constants.unique_index_fields: collection_property.unique_index_fields
                }
            )
            get_data_result: list[CollectionData] | ReturnCode = \
                await self.clients[databaseConfig.name].ShCommandAsync(get_collection_data_query, CollectionData)

            #if unsuccessful it will give a ReturnCode
            if isinstance(get_data_result, ReturnCode): return get_data_result
            
            #create collection folder
            collection_folder = f"{database_folder}/{collection_property.name}"
            os.makedirs(collection_folder, exist_ok=True)

            #generate script from template and write to file
            compare_insert_template = self.templates.get_template(TemplatesFiles.compare_insert)
            for documents_data in get_data_result:
                compare_insert_command = await compare_insert_template.render_async(
                    {
                        Constants.db_name: databaseConfig.destination_db,
                        Constants.coll_name: collection_property.name,
                        Constants.source_data_json: json.dumps(documents_data.value, indent=2),
                        Constants.unique_fields: json.dumps(documents_data.key, indent=2)
                    }
                )

                #write the generated document-level query to a file
                documentFile = f'{collection_folder}/{documents_data.filename}.js'
                with open(documentFile, 'w+') as document_file:
                    document_file.write(compare_insert_command)

            utils.complete_richtask(
                collection_weave_task, 
                f"build weave queries for collection: {collection_property.name}"
            )
            self.logger.debug(f"form_documentsdata_async Complete: {databaseConfig.source_db} | {collection_property.name}")
            return ReturnCode.SUCCESS
        except Exception as ex:
            self.logger.fatal(f"Unknown error occurred while weaving. {ex}")


