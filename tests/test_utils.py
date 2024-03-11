import os
import pytest
from mongocd.Core import utils

# pytestmark = pytest.mark.skip("all tests still WIP")

@pytest.mark.parametrize("path_name", ["Core"])
def test_get_full_path(path_name):
    fullPath = utils.get_full_path(path_name)
    print("Fullpath ", fullPath)
    assert os.path.isabs(fullPath)

@pytest.mark.parametrize("zip_url", 
    ["https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-zip-file.zip",
     "https://github.com/hayone1/MongoPrismSync/releases/download/v1alpha1_v0.0.1/templates_v1alpha1.zip"])
def test_download_and_extract_zip(zip_url):
    folder = utils.get_full_path("tests/debug/outputs/templates")
    print("Fullpath ", folder)
    success_result = utils.download_and_extract_zip(zip_url, folder)
    assert success_result == True
    assert len(os.listdir(folder)) > 0