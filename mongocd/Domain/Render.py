

from logging import Logger
import os
from typing import Any, Generator
from kink import di
from pydantic import BaseModel, ValidationInfo, field_validator, model_validator
from starlark_go import Starlark
from accessify import private
from mongocd.Domain.Base import Constants, FileStructure, ReturnCode
from mongocd.Domain.Database import DocumentData
from mongocd.Domain.PostRender import PostRenderer
from mongocd.Core import utils


class StarlarkContext:
    resource_list: dict
    environment: dict

    def __init__(self, items: list[dict],
            variables: dict, env: dict) -> None:
        self.resource_list = {}
        self.resource_list['items'] = items
        self.resource_list['functionConfig'] = {}
        # both data and params do the same thing
        self.resource_list['functionConfig']['data'] = variables
        self.resource_list['functionConfig']['params'] = variables
        self.environment = env

class StarlarkRun(BaseModel):
    """Validates Document using stalark"""
    selectors: list[dict] = []
    exclude: list[dict] = []
    configMap: dict = {
        "source": ""
    }
    configPath: str = ""


    def validate(self, source_documents: list[DocumentData]
            ) -> ReturnCode:
        """
        Applies the starlark validation code to the documents
        """
        intrepreter = Starlark()
        # intrepreter.exec(StarlarkContext)
        overlay_folder_path = f"{di['config_folder_path']}/{FileStructure.OVERLAYSFOLDER}"
        for documentdata in source_documents:
            is_match: bool
            try:
                # check if document matches any of the selectors
                if len(self.selectors) == 0:
                    # default to true if selector is empty
                    is_match = True
                else:
                    is_match = any([
                        utils.match_document(
                            vars(documentdata), filter_dict
                        ) for filter_dict in self.selectors
                        
                    ])
                    # print(f"data selector matched {is_match} |selector: {self.selectors} |data: {vars(documentdata)}")
                # if any document in the exclude matches then
                # set is_match to false
                if len(self.exclude) > 0:
                    is_match = not any([
                        utils.match_document(
                            vars(documentdata), filter_dict
                        ) for filter_dict in self.exclude
                    ])

                # yield document unmodified
                if not is_match:
                    continue
                # print(f"reached x, data: {documentdata.data}")
                result = self.apply_script(
                    documentdata.data, overlay_folder_path, intrepreter
                )
                # print(f"reached xx, data: {documentdata.data}")
                return result
            except Exception as ex:
                di[Logger].error(
                    "Error occurred while validating data"
                    f"for {documentdata.key} | {type(ex)} | {ex}"
                )
                return ReturnCode.VALIDATION_ERROR
        di[Logger].warning(f"No document match found for selectors: {self.selectors}")
        return ReturnCode.SUCCESS
    @private
    def apply_script(self, document: dict,
            overlay_folder_path: str, intrepreter: Starlark) -> ReturnCode:
        """Apply the starlark script to the document's data"""
        # if path is specifieed
        variables: dict
        source: str
        if not utils.is_empty_or_whitespace(self.configPath):
            overlay_file_path = f"{overlay_folder_path}/{self.configPath}"
            source, variables = self.get_source_from_file(overlay_file_path)
        else:
            variables = self.configMap
            source = self.configMap['source']
            # remove source from variables
            del variables['source']
        
        # https://pypi.org/project/starlark-go/
        try:
            # intrepreter.exec(
            #     f"ctx = StarlarkContext({[document]},{variables},{vars(os.environ.items())})")
            ctx = StarlarkContext([document], variables, dict(os.environ))
            # print(f"reached yy: {vars(ctx)}")
            #ToDo: Document that the ctx is passed as a frozen object
            # and connot be modified from within the script
            # https://docs.bazel.build/versions/5.4.1/skylark/language.html
            intrepreter.exec(f"ctx = {vars(ctx)}")
            intrepreter.exec(source)
            intrepreter.eval("main()")
            return ReturnCode.SUCCESS
        except Exception as ex:
            di[Logger].error(f"Validation or Execution Error in StarLarkRun: {type(ex)} | {ex}")
            return ReturnCode.VALIDATION_ERROR
        
    
    def get_source_from_file(file_path: str) -> tuple[str, dict]:
        """Returns a tuple of (source, variables) needed for starlark script"""
    # get the variables and source
        if file_path.endswith('.star'):
            with open(file_path, 'r') as file:
                return file.read(), {}
        else:
            config = utils.load_data_from_file(file_path)
            if config['kind'] == 'StarlarkRun':
                return config['source'], config['params']
            elif config['kind'] == 'ConfigMap':
                variables = config['data']
                source = config['data']['source']
                # remove source from variables
                del variables['source']
                return source, variables


class CueValidator(BaseModel):
    selectors: list[dict] = []
    configMap: dict = {
        "source": ""
    }
    configPath: str = ""

    @field_validator('configMap')
    @classmethod
    def validate_configMap(cls, value: dict, info: ValidationInfo):
        '''Validate the patch string provided is valid'''
        if len(value) > 0:
            assert Constants.source.value in value, \
                f"field missing, must include 'source: |' field in CueValidator object"
        return value
    
    @model_validator(mode='after')
    def validate_exclusive_config(self) -> 'CueValidator':
        '''Validate that configMap and configPath are not specified at the same time'''
        assert (len(self.configMap) == 0
            or utils.is_empty_or_whitespace(self.configPath)), \
            ("Both configMap and configPath cannot be specified in the same "
             "CueValidator Object")
        return self


class Validator(BaseModel):
    cue: CueValidator | dict = CueValidator()
    # default to none to encourage use of kustomize
    starlarkrun: StarlarkRun | dict = {}

    @model_validator(mode='after')
    def validate_exclusive_postrenders(self) -> 'PostRenderer':
        assert (self.cue == {} or self.starlarkrun == {}), \
            ("Both cue and starlark cannot be specified in the same "
             "Validator Object")
        return self

class EnvironmentRenderer(BaseModel):
    # type: str = "json",
    postRenderers: list[PostRenderer] = [PostRenderer()]
    exclude: list[dict] = []
    validators: list[Validator] = [Validator()]