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
            collection_property: CollectionProperty, database_folder: str,
            top_level_commands: str) -> ReturnCode:
        pass

    
class IDatabaseService:
    '''
    responsible for pulling from source db and weaving into a useable form for destination db
    '''
    # @abstractmethod
    async def generate_syncscripts_async(self):
        pass
class IPostRendererService:
    '''
    uses kustomize patch/Helm PostRender like features to customize the weaved data.
    '''
    def generate_changeset(source_data: dict, destination_data: dict):
        '''
        Generates a list of changes that need to be applied to the source_data
        in order to arrive at the destinaton_data
        '''
        pass

    # def filter_resources(target_selector: dict)

    def generate_from_patches(source_data: dict, patches: list[dict] | str) -> dict:
        '''
        Generates a dictionary that results from applying the given patches to the
        source_data.
        '''
        pass

    def generate_from_starlark(source_data: dict, starlark):
        '''
        Generates a dictionary that results from applying the given starlark script
        to the source_data.
        '''
        pass