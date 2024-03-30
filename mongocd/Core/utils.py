
import json
from logging import Logger
import os
from pathlib import Path
import traceback
from typing import Any, Generator
from zipfile import ZipFile
from kink import di, inject
from requests.exceptions import ConnectionError
from rich.progress import Progress, TaskID
from rich import print


import requests
import yaml
from mongocd.Domain.Base import Constants, Messages, ReturnCode

# @staticmethod
# def conform_path(input_path: str):
#     '''Ensure the path is os compliant'''
#     converted_path = os.path.join(*input_path.split("\\"))
#     return os.path.normpath(converted_path)

@staticmethod
def is_empty_or_whitespace(input_string: str):
    """Returns True if object is a string that is empty or contains white space alone"""
    if not isinstance(input_string, str|None):
        raise TypeError("object is not a valid string")
    return input_string is None or input_string.strip() == ''

@staticmethod
def get_full_path(input_path) -> str:
    """
    Get the absolute path of a given path

    Path will remain unchanged if already absolute
    """
    #convert the path into a format compliant with the underlying os
    input_path = os.path.join(*input_path.split("\\"))
    input_path = os.path.normpath(input_path)
    # If the input path is absolute, return it unchanged
    if os.path.isabs(input_path):
        return input_path
    else:
        # If the input path is relative, get the absolute path
        current_directory = os.getcwd()
        full_path = os.path.abspath(os.path.join(current_directory, input_path))
        return full_path
    
@staticmethod
@inject
def complete_richtask(task_id: TaskID, description: str, progress: Progress = None):
    """replaces task with completed message.
    progress object is gotten from injected Progress.
    
    Throws error if progress object is not injected"""
    progress.update(task_id, completed=True)
    progress.remove_task(task_id)
    # progress.stop()
    print(f"[green]✓[/green] {description}")

def fault_richtask(task_id: TaskID, description: str, progress: Progress = None):
    """replaces task with faulted message.
    progress object is gotten from injected Progress.
    
    Throws error if progress object is not injected"""
    progress.update(task_id, completed=True)
    progress.remove_task(task_id)
    # progress.stop()
    print(f"[red]x[/red] {description}")

@staticmethod
def download_and_extract_zip(zip_url: str, extract_folder: str) -> ReturnCode:
    """Download and extract a zip file to specified folder

    Make sure logger has been initialized for dependency injection
    """
    logger = di[Logger]
    # Create the extraction folder if it doesn't exist
    os.makedirs(extract_folder, exist_ok=True)

    # Download the zip file
    try:
        response = requests.get(zip_url, timeout=Constants.general_timeout.value)
        if response.status_code == 404:
            logger.error(f"No Resource Found at {zip_url}")
            return False
        zip_file_path = os.path.normpath(
            os.path.join(extract_folder, 'downloaded_file.zip'))

        logger.debug(f"Working on file: {zip_file_path}")
        logger.debug(Messages.write_file)
        with open(zip_file_path, 'wb') as zip_file:
            zip_file.write(response.content)

        # Extract the contents
        logger.debug(Messages.extract_file)
        with ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        # Remove the downloaded zip file
        logger.debug(Messages.remove_file)
        os.remove(zip_file_path)
    except ConnectionError as ex:
        logger.error(f"{ReturnCode.CONNECTION_ERROR}: Unable to fetch latest templates, please check that you have an active internet connection. {ex}")
        return ReturnCode.CONNECTION_ERROR
    except Exception as ex:
        logger.error(f"""{ReturnCode.UNKNOWN_ERROR.name}: Unknown error occurred while 
                     {Messages.write_file} or {Messages.extract_file} or {Messages.remove_file} | {ex} | {traceback.format_exc()}""")
        return ReturnCode.UNKNOWN_ERROR
    logger.debug(f"Download and Extract Successful: {zip_url} | destination: {extract_folder}")
    return ReturnCode.SUCCESS

@staticmethod
def replace_nth_path_name(path_str: str, n: int, new_name: str):
    """
    Replaces the nth path name at n in a path-like string with a new name.
    

    Args:
        path_str (str): The path-like string.
        n (int): The position of the path name to replace (counting from the end).
        new_name (str): The new name to use.

    Returns:
        str: The new path-like string with the replaced name.

    Raises:
        ValueError: If n is less than 1 or greater than the number of path components.
    Remarks:
        Use a negative index to replace the nth path relative to the end
    """

    path = Path(path_str)
    components = list(path.parts)

    if abs(n) < 1 or abs(n) > len(components):
        raise ValueError(f"Invalid position: {n}")

    components[n] = new_name
    return Path(*components)

@staticmethod
def filter_dicts(source_dict_list: list[dict],
        dict_filter: dict,) -> Generator[dict, Any, None]:
    # filtered_dicts = []
    for source_dict in source_dict_list:
        if all(key in source_dict and source_dict[key] == value
               for key, value in dict_filter.items()):
            yield source_dict
@staticmethod
def multi_filter_dicts(dict_filters: list[dict],
        source_dict_list: list[dict]) -> list[dict]:
    """Lazy function"""
    # woud have been nice to have a linq like function to build this
    # function as a pipeline ish
    filtered_dicts_lists: list[list[dict]] = []
    for dict_filter in dict_filters:
        filtered_dicts_lists.append(filter_dicts(source_dict_list, dict_filter))

    flattened_filtered_dicts = [dict_item for sublist in filtered_dicts_lists
                                for dict_item in sublist]
    
    # Convert the list of dictionaries to a set of tuples for uniqueness
    unique_tuples = {tuple(sorted(d.items())) for d in flattened_filtered_dicts}

    # Convert the unique tuples back to dictionaries
    unique_dicts = [dict(t) for t in unique_tuples]
    return unique_dicts

@staticmethod
def match_document(document_dict: dict, filter_dict: dict) -> bool:

    # return true if there is no filter
    filter_dict = filter_dict.copy()
    if len(filter_dict) == 0:
        return True
    #match and delete matching meta filter keys
    for key, value in document_dict.items():
        # data not a part of meta data
        if key == 'data':
            continue
        
        if key in filter_dict and isinstance(value, dict):
            if not match_filter(value, filter_dict[key]):
                return False
            #else
            del filter_dict[key]
        elif key in filter_dict:
            #key is same but value is not
            if filter_dict[key] != value:
                return False
            # else remove from remaining filters
            del filter_dict[key]

    # match the remaining filters (data filter). Potential issue is if there
    # is a data filter that is reserved as part of the meta filter keys.
    if not match_filter(document_dict['data'], filter_dict):
        return False
    return True

@staticmethod
def match_filter(data: dict, filter_dict: dict, exclude_keys: list = None) -> bool:
    """
    Returns True if data matches filter(via a recursive check) otherwise returns False

    Args:
        exclude_keys: keys to exclude from match checking
    """
    if exclude_keys is None:
        exclude_keys = []
    if not isinstance(filter_dict, dict) or not isinstance(data, dict):
        return False
    # print(f"filter_dict: {filter_dict}")
    for key, value in filter_dict.items():
        # print(f"matching {key}")
        if key in exclude_keys:
            continue # don't check
        if key not in data:
            return False
        if isinstance(value, dict):
            if not match_filter(data[key], value):
                return False
        elif value != data[key]:
            return False
    return True

@staticmethod
def load_data_from_file(file_path: str) -> dict:
    """Loads a dictionary or list from a json or yaml file"""
    logger = di[Logger]
    if not os.path.exists(file_path):
        logger.error(
            "Unable to load file, it does not exist "
            f"or is inaccessible: {file_path}")
        return ReturnCode.DIR_ACCESS_ERROR
    with open(file_path, 'r') as file:
        try:
            # Attempt to load JSON first (more common for kustomize patches)
            return json.load(file)
        except json.JSONDecodeError:
            pass
        # flow into yaml if json didnt work
        try:
            return yaml.safe_load(file_path)
        except yaml.YAMLError:
            logger.error(f"Failed to parse file '{file_path}' as JSON or YAML")
            return ReturnCode.INVALID_CONFIG_ERROR
@staticmethod
def load_data_from_string(data: str) -> list | dict:
    """Loads a dictionary or list from a json or yaml string"""
    logger = di[Logger]
    try:
        # Attempt to load JSON first (more common for kustomize patches)
        return json.loads(data)
    except json.JSONDecodeError:
        pass
    # flow into yaml if json didnt work
    try:
        return yaml.safe_load(data)
    except yaml.YAMLError:
        logger.error(f"Failed to parse given string as JSON or YAML: '{data}'")
        return ReturnCode.INVALID_CONFIG_ERROR


            
    