from logging import Logger

from jinja2 import Environment
from mongocd.Interfaces.Services import ICollectionService
from mongocd.Domain.Database import *
from mongocd.Domain.Base import *

class CollectionService(ICollectionService):
    def __init__(self, templates: Environment, mongoMigration: MongoMigration, clients: dict[str, DbClients], logger: Logger):
            self.logger = logger
            self.templates = templates
            self.mongoMigration = mongoMigration
            self.clients = clients
            # self.template_folder = FileStructure.TEMPLATESFOLDER

    async def FormDocumentsDataAsync(self, databaseConfig: DatabaseConfig,
                            collection_property: CollectionProperty, database_folder: str) -> ReturnCode:

        self.logger.debug(f"FormCollectionDataAsync Started: {databaseConfig.source_db} | {collection_property.name}")
        #get data from source collection
        get_collection_data_template = self.templates.get_template(TemplatesFiles.getCollectionData)
        get_collection_data_query = await get_collection_data_template.render_async(
             {
                  Constants.db_name: databaseConfig.source_db,
                  Constants.coll_name: collection_property.name,
                  Constants.unique_index_fields: collection_property.unique_index_fields
             }
        )
        get_data_result: list[CollectionData] | ReturnCode = await self.clients[databaseConfig.name].ShCommandAsync(get_collection_data_query)

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
                    Constants.unique_fields: json.dumps(documents_data.unique_fields, indent=2)
                }
            )

            #write the generated document-level query to a file
            documentFile = f'{collection_folder}/{documents_data.filename}.js'
            with open(documentFile, 'w+') as document_file:
                document_file.write(compare_insert_command)

        self.logger.debug(f"FormDocumentsDataAsync Complete: {databaseConfig.source_db} | {collection_property.name}")
        return ReturnCode.SUCCESS


