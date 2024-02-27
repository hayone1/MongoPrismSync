
import os
from zipfile import ZipFile

import requests
from mongoprism import logger


@staticmethod
def get_full_path(input_path) -> str:
    # If the input path is absolute, return it unchanged
    if os.path.isabs(input_path):
        return input_path
    else:
        # If the input path is relative, get the absolute path
        current_directory = os.getcwd()
        full_path = os.path.abspath(os.path.join(current_directory, input_path))
        return full_path
    
@staticmethod
def download_and_extract_zip(zip_url, extract_folder):
    # Create the extraction folder if it doesn't exist
    os.makedirs(extract_folder, exist_ok=True)

    # Download the zip file
    response = requests.get(zip_url)
    print("StatusCode",response.status_code)
    if response.status_code == 404:
        logger.error(f"No Resource Found at {zip_url}")
        raise FileNotFoundError(f"No Resource Found at {zip_url}")
    zip_file_path = os.path.join(extract_folder, 'downloaded_file.zip')

    with open(zip_file_path, 'wb') as zip_file:
        zip_file.write(response.content)

    # Extract the contents
    with ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    # Remove the downloaded zip file
    os.remove(zip_file_path)