from logging import Logger
from mongocd.Interfaces.Services import ICollectionService
from mongocd.Domain.Database import *
from mongocd.Domain.Base import *

class CollectionService(ICollectionService):
    def __init__(self, mongoMigration: MongoMigration, clients: dict[str, DbClients], logger: Logger):
            self.logger = logger
            self.mongoMigration = mongoMigration
            self.clients = clients
            # self.template_folder = FileStructure.TEMPLATESFOLDER

    async def GenerateCreateIndexCommandAsync(self, databaseConfig: DatabaseConfig, collection_property: CollectionProperty) -> CollectionCommand:
        self.logger.debug(f"Creating CreateCollectionIndexCommand Started: {databaseConfig.source_db} | {collection_property.name}")

        sourceIndices = await self.clients[databaseConfig.name].ShCommandAsync(
            f'db.getSiblingDB("{databaseConfig.source_db}")["{collection_property.name}"].getIndexes()')
        
        async with aiofiles.open(f'{FileStructure.TEMPLATESFOLDER}/{TemplatesFiles.copyIndices}', 'r') as file:
            self.logger.info(f"Creating CreateCollectionIndexCommand Ended: {databaseConfig.source_db} | {collection_property.name}")
            result = CollectionCommand(name=collection_property.name, 
                command=(await file.read()) \
                    .replace('___dbName___', databaseConfig.destination_db) \
                    .replace('___collName___', collection_property.name) \
                    .replace('__sourceIndices__',json.dumps(sourceIndices)))
            return result


