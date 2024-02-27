import os
import pytest
from mongoprism.core import utils

@pytest.mark.parametrize("path_name", ["core"])
def test_get_full_path(path_name):
    fullPath = utils.get_full_path(path_name)
    print("Fullpath ", fullPath)
    assert os.path.isabs(fullPath)

@pytest.mark.parametrize("zip_url", 
    ["https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-zip-file.zip"])
def test_download_and_extract_zip(zip_url):
    folder = utils.get_full_path("tests/debug/outputs/templates")
    print("Fullpath ", folder)
    utils.download_and_extract_zip(zip_url, folder)
    assert len(os.listdir(folder)) > 0