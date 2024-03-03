from abc import ABC, abstractmethod

from mongocd.Domain.Database import *

class IVerifyService(ABC):

    @abstractmethod
    def VerifyConnectivity(mongoMigration: MongoMigration) -> bool:
        '''[Injected]: mongoMigration'''
        pass

    @abstractmethod
    def VerifyDatabases(databaseConfig: list[DatabaseConfig]):
        pass

class IIndexService:
    pass

class ICollectionService:
    @abstractmethod
    async def CreateCollectionIndexCommandAsync(databaseConfig: DatabaseConfig, collection_property: CollectionProperty) -> CollectionCommand:
        pass

    @abstractmethod
    async def GetSourceCollectionsAsync(databaseConfig: DatabaseConfig, commandsList: DatabaseSyncScripts,
                         collection_property: CollectionProperty, get_data_query_template: str, compareCopy_query_template: str):
        pass

    @abstractmethod
    async def SaveCollectionsCommandsAsync(databaseOutputFolder: str, collectionName: str, collectionScripts: list[DatabaseSyncScripts]):
        pass

    @abstractmethod
    async def GenerateSyncScriptsAsync(databaseConfig: DatabaseConfig):
        pass

    
    #==========Synchronous methods===============
    @abstractmethod
    def CreateCollectionIndexCommand(databaseConfig: DatabaseConfig, collection_property: CollectionProperty) -> CollectionCommand:
        pass

    @abstractmethod
    def GetSourceCollections(databaseConfig: DatabaseConfig, commandsList: DatabaseSyncScripts,
                         collection_property: CollectionProperty, get_data_query_template: str, compareCopy_query_template: str):
        pass

    @abstractmethod
    def SaveCollectionsCommands(databaseOutputFolder: str, collectionName: str, collectionScripts: list[DatabaseSyncScripts]):
        pass

    @abstractmethod
    def GenerateSyncScripts(databaseConfig: DatabaseConfig):
        pass

    
class IDatabaseService:
    @abstractmethod
    async def GenerateSyncScriptsAsync(databaseConfig: DatabaseConfig):
        pass

    #==========Synchronous methods===============
    @abstractmethod
    async def GenerateSyncScripts(databaseConfig: DatabaseConfig):
        pass