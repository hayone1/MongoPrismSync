from abc import ABC, abstractmethod

from mongocd.Domain.Database import *
from mongocd.Domain.Base import *
class IVerifyService():

    # @abstractmethod
    def verify_connectivity(self, source_password: str) -> ReturnCode:
        '''Verify Connectivity to the mongodb instance'''
        pass

    # @abstractmethod
    def verify_databases(self) -> ReturnCode:
        '''Verify connectivity to the databases listen in the weaveconfig'''
        pass

# class IIndexService:
#     pass

class ICollectionService:

    # @abstractmethod
    async def form_documentsdata_async(self, databaseConfig: DatabaseConfig,
            collection_property: CollectionProperty, database_folder: str) -> ReturnCode:
        pass

    
class IDatabaseService:
    # @abstractmethod
    async def generate_syncscripts_async(self):
        pass

    # @abstractmethod
    # async def GenerateIndexReplicationCommandAsync(databaseConfig: DatabaseConfig, collection_property: CollectionProperty) -> CollectionCommand:
    #     pass