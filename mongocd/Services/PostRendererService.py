
from logging import Logger
from typing import Any, Generator
import jsonpatch
from jsonpatch import JsonPatch
from kink import inject
from accessify import implements, private
from mongocd.Domain.Database import DocumentData, DatabaseConfig
from mongocd.Interfaces.Services import IPostRendererService

@inject
@implements(IPostRendererService)
class PostRendererService:

    def __init__(self, logger: Logger):
        self.logger = logger

    def generate_changeset(self, source_data: dict,
        destination_data: dict, document_id: str) -> JsonPatch:
        try:
            return jsonpatch.make_patch(source_data, destination_data)
        except Exception as ex:
            self.logger.error(
                "Error occurred while attempting to generate changeset"
                f"for {document_id} | {type(ex)} | {ex}"
            )

    def generate_from_starlark(self, source_data: dict, starlark, document_id: str):
        '''
        Generates a dictionary that results from applying the given starlark script
        to the source_data.
        '''
        try:
            pass
        except Exception as ex:
            self.logger.error(
                "Error occurred while attempting to apply starlark to source_data"
                f"for {document_id} | {type(ex)} | {ex}"
            )

    # @private
    # def filter_collectiondata(collectiondata_list: list[DocumentData],
    #         dict_filter: dict,) -> Generator[dict, Any, None]:
    #     for collection_data in collectiondata_list:
    #         if all(key in collection_data.value and collection_data.value[key] == value
    #             for key, value in dict_filter.items()):
    #             yield collection_data.value