
from logging import Logger
import os
from typing import Any, Generator
from kink import di, inject
from pydantic import BaseModel, ValidationInfo, field_validator, model_validator
import yaml
import jsonpatch
from jsonpatch import JsonPatch

from mongocd.Core import utils
from mongocd.Domain.Database import DocumentData


class Options(BaseModel):
    # allowIdChange: bool = True
    # which ever object has default will be run first
    # else order will be cshose randomly
    default: bool = False

class Patch(BaseModel):
    target: dict = dict()
    # patch should either be 
    patch: str = ""
    path: str = ""
    options: Options = Options()
    
    @field_validator('patch')
    @classmethod
    def validate_patch(cls, value: str, info: ValidationInfo):
        '''Validate the patch string provided is valid'''
        assert isinstance(yaml.load(value), list[dict]), f"patch format is invalid: f{value}"
        return value
    
    @model_validator(mode='after')
    @classmethod
    def validate_exclusive_patch(self) -> 'Patch':
        '''Validate that patch and path are exclusively specified'''
        assert (utils.is_empty_or_whitespace(self.patch)
            or utils.is_empty_or_whitespace(self.path)), \
            ("Both path and patch cannot be specified in the same "
             "patch Object")


# ToDo: https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/replacements/
class Replacement(BaseModel):
    pass

class Kustomize(BaseModel):
    patches: list[Patch] = [Patch()]

    #pass the class members to BaseModel
    def __init__(self, data):
        super().__init__(**data)

    @inject
    def apply_patch(self, source_data: list[DocumentData], patch: str, data_id: str, config_folder_path = None) -> dict:
        '''
        Generates a dictionary that results from applying the given patches to the
        source_data.
        Patches should be valid json patch string or list
        
        Args:
            data_id: unique document key/id that can be used to identify the document
        '''
        transformed_data: list[DocumentData] = []
        try:
            for curr_patch in self.patches:
            
            if not (utils.is_empty_or_whitespace(curr_patch.path)):
                path_yaml = os.path.abspath(
                    os.path.join(config_folder_path, curr_patch.path))

            patch_json = jsonpatch.JsonPatch(yaml.load(patch))
            return jsonpatch.apply_patch(source_data, patch_json)
        except Exception as ex:
            di[Logger].error(
                "Error occurred while attempting to apply patch to source_data"
                f"for {data_id} | {type(ex)} | {ex}"
            )

    def filter_documents(source_data: list[DocumentData],
        dict_filter: dict) -> Generator[dict, Any, None]:
        for document_data in source_data:
            if all(key in document_data.value and document_data.value[key] == value
                for key, value in dict_filter.items()):
                yield document_data

# advise people to use starlark for data tests and validation
class Starlark(BaseModel):
    data: dict = dict()
    options: Options = Options()
    source: str = ""

class PostRenderer(BaseModel):
    kustomize: Kustomize = Kustomize()
    # default to none to encourage use of kustomize
    starlark: Starlark = None

    @model_validator(mode='after')
    @classmethod
    def validate_exclusize_postrenders(self) -> 'PostRenderer':
        assert (self.kustomize is None
            or self.starlark is None), \
            ("Both kustomize and starlark cannot be specified in the same "
             "postRenderer Object")