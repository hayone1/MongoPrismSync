from abc import ABC, abstractmethod

from mongocd.Domain.Database import *
from mongocd.Domain.Base import *
class IVerifyService(ABC):

    @abstractmethod
    def verify_connectivity(self, source_password: str) -> ReturnCodes:
        '''Verify Connectivity to the mongodb instance'''
        pass

    @abstractmethod
    def verify_databases(self) -> ReturnCodes:
        '''Verify connectivity to the databases listen in the weaveconfig'''
        pass

# class IIndexService:
#     pass

class ICollectionService:
    @abstractmethod
    async def GenerateCreateIndexCommandAsync(databaseConfig: DatabaseConfig, collection_property: CollectionProperty) -> CollectionCommand:
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

    
class IDatabaseService:
    @abstractmethod
    async def GenerateSyncScriptsAsync(databaseConfig: DatabaseConfig):
        pass

    #==========Synchronous methods===============
    @abstractmethod
    async def GenerateSyncScripts(databaseConfig: DatabaseConfig):
        pass