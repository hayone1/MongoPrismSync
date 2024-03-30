import os
import pytest
from mongocd.Core.utils import (
    get_full_path, download_and_extract_zip,
    replace_nth_path_name, match_filter,
    match_document
)
from mongocd.Domain.Base import ReturnCode

# pytestmark = pytest.mark.skip("all tests still WIP")

@pytest.mark.parametrize("path_name", ["Core"])
def test_get_full_path(path_name):
    fullPath = get_full_path(path_name)
    # print("Fullpath ", fullPath)
    assert os.path.isabs(fullPath)

@pytest.mark.skip(reason="Requires download action every time")
@pytest.mark.parametrize("zip_url", 
    ["https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-zip-file.zip",
     "https://github.com/hayone1/MongoPrismSync/releases/download/v1alpha1_v0.0.1/templates_v1alpha1.zip"])
def test_download_and_extract_zip(zip_url):
    folder = get_full_path("tests/debug/outputs/templates")
    print("Fullpath ", folder)
    success_result = download_and_extract_zip(zip_url, folder)
    assert success_result == ReturnCode.SUCCESS
    assert len(os.listdir(folder)) > 0

def test_replace_nth_path_name():
    """Test that the nth path name is replaced with a new name"""
    path_str = "/home/user/data/folder1/folder2/file.txt"
    n = -2
    new_name = "replaced_folder"
    expected_result = "/home/user/data/folder1/replaced_folder/file.txt"

    result = replace_nth_path_name(path_str, n, new_name)

    assert str(result) == os.path.normpath(expected_result)

def test_match_filter():
    filter = { 'a': 1, 'b': { 'c': 2 } }
    data = { 'a': 1, 'b': { 'c': 2, 'd': 3 }, 'e': 4 }
    assert match_filter(data, filter) is True, \
        "Valid data not treated as valid"

    invalid_filter = "this_is_a_string"
    assert match_filter(invalid_filter, data) is False, \
        "invalid_filter not treated as invalid "
# @pytest.mark.skip
def test_match_document(planet_mercury):
    filter = {'collection': 'planets', "hasRings": False}
    assert match_document(planet_mercury, filter) is True, \
        "Valid data not treated as valid"