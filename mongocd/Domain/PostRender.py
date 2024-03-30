
import json
from logging import Logger
from typing import Any, Generator
from kink import di
from pydantic import BaseModel, ValidationInfo, field_validator, model_validator
import yaml
from jsonpatch import JsonPatch
from accessify import private


from mongocd.Core import utils
from mongocd.Domain.Base import FileStructure, ReturnCode
from mongocd.Domain.Database import DocumentData


# class Options(BaseModel):
#     # allowIdChange: bool = True
#     # which ever object has default will be run first
#     # else order will be cshose randomly
#     default: bool = False


class Patch(BaseModel):
    target: dict = {}
    # patch should either be 
    patch: str = ""
    path: str = ""
    # options: Options = Options()
    
    @field_validator('patch')
    @classmethod
    def validate_patch(cls, value: str, info: ValidationInfo):
        """Validate the patch string provided is valid"""
        assert (utils.is_empty_or_whitespace(value)
                or isinstance(yaml.safe_load(value), list|dict)
                or isinstance(json.loads(value), list|dict)
                ), \
                f"patch format is invalid: f{value}"
        return value
    
    @model_validator(mode='after')
    def validate_exclusive_patch(self) -> 'Patch':
        """Validate that patch and path are not specified at the same time"""
        assert (utils.is_empty_or_whitespace(self.patch)
            or utils.is_empty_or_whitespace(self.path)), \
            ("Both path and patch cannot be specified in the same "
             "patch Object")
        return self


# ToDo maybe: https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/replacements/
class Replacement(BaseModel):
    pass

class Kustomize(BaseModel):
    """Exposes kustomize features"""
    patches: list[Patch] = [Patch()]

    # pass the class members to BaseModel
    # does this work?
    # def __init__(self, data):
    #     super().__init__(**data)

    # @inject
    def apply(self, source_documents: list[DocumentData]
            ) -> Generator[DocumentData, Any, ReturnCode | None]:
        """
        Generates a dictionary that results from applying the given patches to the
        source_data.
        Patches should be valid json patch string or list
        
        """
        overlay_folder_path = f"{di['config_folder_path']}/{FileStructure.OVERLAYSFOLDER}"
        # update each document data until it passees through all the patches
        # ToDo: How to make this more efficient
        for documentdata in source_documents:
            patch_result = self.apply_patch(
                documentdata, overlay_folder_path
            )
            if isinstance(patch_result, ReturnCode):
                return patch_result
            #else
            documentdata.data = patch_result
            yield documentdata
    @private
    def apply_patch(self, documentdata: DocumentData,
            overlay_folder_path: str) -> dict | ReturnCode:
        """
        Passes the document through the patches to arrive at a final
        patched document.
        """
        # convert to dictionary
        document_dict = vars(documentdata)
        # Important: The input to each iteration of patch will be
        # from the output of the previous patch
        for patch in self.patches:
            # print(f"patch target: {patch.target}")
            if not utils.match_document(document_dict, patch.target):
                continue # skip this patch
            # print(f"source document matched: {document_dict}")
            # else
            patch_operations: list | dict
            #if path is specified
            if not utils.is_empty_or_whitespace(patch.path):
                overlay_file_path = f"{overlay_folder_path}/{patch.path}"
                patch_operations = utils.load_data_from_file(overlay_file_path)
            # if patch is specified inline
            elif not utils.is_empty_or_whitespace(patch.patch):
                patch_operations = utils.load_data_from_string(patch.patch)
            # error
            if isinstance(patch_operations, ReturnCode):
                return patch_operations

            #update data with patch
            try:
                # Inline Strategic Merge
                if isinstance(patch_operations, list):
                    #json op patch
                    document_dict['data'] = \
                        JsonPatch(patch_operations).apply(document_dict['data'])
                # Inline JSON6902
                if isinstance(patch_operations, dict):
                    #strategic merge patch
                    # enrich patch_operations
                    for key in document_dict['data']:
                        if key not in patch_operations:
                            patch_operations[key] = document_dict['data'][key]
                    document_dict['data'] = \
                        JsonPatch.from_diff(documentdata.data, patch_operations) \
                                .apply(document_dict['data'])
                # print(f"current data: {document_dict['data']}")
            except Exception as ex:
                di[Logger].error(
                    f"Error occurred while attempting to apply patches: {patch_operations} "
                    f"to source_data with key: {documentdata.key} | {type(ex)} | {ex}"
                )
                return ReturnCode.EXECUTION_ERROR

        return document_dict['data']

# advise people to use starlark for data tests and validation

class PostRenderer(BaseModel):
    kustomize: Kustomize | dict = Kustomize()