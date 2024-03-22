import os
import pytest
from mongocd.Core.utils import *

# pytestmark = pytest.mark.skip("all tests still WIP")

@pytest.mark.parametrize("path_name", ["Core"])
def test_get_full_path(path_name):
    fullPath = get_full_path(path_name)
    # print("Fullpath ", fullPath)
    assert os.path.isabs(fullPath)

@pytest.mark.parametrize("zip_url", 
    ["https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-zip-file.zip",
     "https://github.com/hayone1/MongoPrismSync/releases/download/v1alpha1_v0.0.1/templates_v1alpha1.zip"])
def test_download_and_extract_zip(zip_url):
    folder = get_full_path("tests/debug/outputs/templates")
    print("Fullpath ", folder)
    success_result = download_and_extract_zip(zip_url, folder)
    assert success_result == True
    assert len(os.listdir(folder)) > 0

def test_replace_nth_path_name():
    '''Test that the nth path name is replaced with a new name'''
    path_str = "/home/user/data/folder1/folder2/file.txt"
    n = -2
    new_name = "replaced_folder"
    expected_result = "/home/user/data/folder1/replaced_folder/file.txt"

    result = replace_nth_path_name(path_str, n, new_name)

    assert str(result) == os.path.normpath(expected_result)