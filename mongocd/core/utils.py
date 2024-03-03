
from logging import Logger
import os
from pathlib import Path
import traceback
from zipfile import ZipFile
from kink import inject
from requests.exceptions import *


import requests
from mongocd.Domain.Base import Messages, ReturnCodes

# @staticmethod
# def conform_path(input_path: str):
#     '''Ensure the path is os compliant'''
#     converted_path = os.path.join(*input_path.split("\\"))
#     return os.path.normpath(converted_path)

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
def download_and_extract_zip(zip_url: str, extract_folder: str, logger: Logger) -> bool:
    '''Download and extract a zip file to specified folder

    Make sure logger has been initialized for dependency injection
    '''
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

        logger.info(f"Working on file: {zip_file_path}")
        logger.info(Messages.write_file)
        with open(zip_file_path, 'wb') as zip_file:
            zip_file.write(response.content)

        # Extract the contents
        logger.info(Messages.extract_file)
        with ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        # Remove the downloaded zip file
        logger.info(Messages.remove_file)
        os.remove(zip_file_path)
    except ConnectionError as ex:
        logger.error(f"Unable to fetch latest templates, please check that you have an active internet connection. {ex}")
        return False
    except Exception as ex:
        logger.error(f"""{ReturnCodes.UNKNOWN_ERROR.name}: Unknown error occurred while 
                     {Messages.write_file} or {Messages.extract_file} or {Messages.remove_file} | {ex} | {traceback.format_exc()}""")
        return False
    logger.info(f"Download and Extract Successful: {zip_url} | destination: {extract_folder}")
    return True