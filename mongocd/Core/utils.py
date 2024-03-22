
from logging import Logger
import os, importlib
from pathlib import Path
import subprocess
import sys
import traceback
from zipfile import ZipFile
from kink import di, inject
from requests.exceptions import *
from rich.progress import Progress, TaskID
from rich import print


import requests
from typer import Typer
from mongocd.Domain.Base import Messages, ReturnCode
from mongocd.Core import config
from pathlib import Path

# @staticmethod
# def conform_path(input_path: str):
#     '''Ensure the path is os compliant'''
#     converted_path = os.path.join(*input_path.split("\\"))
#     return os.path.normpath(converted_path)

@staticmethod
def is_empty_or_whitespace(input_string: str):
    '''Returns True if object is a string that is empty or contains white space alone'''
    if not isinstance(input_string, str|None): raise TypeError("object is not a valid string")
    return input_string is None or input_string.strip() == ''

@staticmethod
def get_full_path(input_path) -> str:
    '''Get the absolute path of a given path

    Path will remain unchanged if already absolute
    '''
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
    '''replaces task with completed message.
    progress object is gotten from injected Progress.
    
    Throws error if progress object is not injected'''
    progress.update(task_id, completed=True)
    progress.remove_task(task_id)
    # progress.stop()
    print(f"[green]✓[/green] {description}")

def fault_richtask(task_id: TaskID, description: str, progress: Progress = None):
    '''replaces task with faulted message.
    progress object is gotten from injected Progress.
    
    Throws error if progress object is not injected'''
    progress.update(task_id, completed=True)
    progress.remove_task(task_id)
    # progress.stop()
    print(f"[red]x[/red] {description}")

@staticmethod
def download_and_extract_zip(zip_url: str, extract_folder: str) -> bool:
    '''Download and extract a zip file to specified folder

    Make sure logger has been initialized for dependency injection
    '''
    logger = di[Logger]
    # Create the extraction folder if it doesn't exist
    os.makedirs(extract_folder, exist_ok=True)

    # Download the zip file
    try:
        response = requests.get(zip_url)
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
        return False
    except Exception as ex:
        logger.error(f"""{ReturnCode.UNKNOWN_ERROR.name}: Unknown error occurred while 
                     {Messages.write_file} or {Messages.extract_file} or {Messages.remove_file} | {ex} | {traceback.format_exc()}""")
        return False
    logger.debug(f"Download and Extract Successful: {zip_url} | destination: {extract_folder}")
    return True

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