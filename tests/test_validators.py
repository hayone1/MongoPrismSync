

# Applies the starlark script to the document's data when configPath is not specified
from mongocd.Domain.Base import ReturnCode
from mongocd.Domain.Render import StarlarkRun

# pytestmark = pytest.mark.skip("all tests still WIP")

def test_starlarkrun_apply_script_no_config_path(mercury_documentdata):
    # Initialize the class object
    starlark_run = StarlarkRun(
        selectors  = [
            {"collection":"planets", "hasRings": False}
        ],
        configMap = {
            "mainAtmosphere": ["thin", "undetectable"],
            "source": """
def main():
    atmosphere = ctx['resource_list']["functionConfig"]["data"]["mainAtmosphere"]
    atmosphere1 = ctx['resource_list']["functionConfig"]["params"]["mainAtmosphere"]
    resource = ctx['resource_list']['items'][0]
    
    if not all([atm in resource["mainAtmosphere"] for atm in atmosphere]):
        fail("atmosphere items [0]", atmosphere, \
            " missing from resource ", resource)
    if atmosphere1[0] not in resource["mainAtmosphere"]:
        fail(atmosphere1[0], " is missing from resource ", resource)
"""
        }
    )

    # Invoke the apply_script method
    result = starlark_run.validate([mercury_documentdata])
    print(f"starlark_run result: {result}")
    # Assert that the result is a dictionary or ReturnCode
    assert result == ReturnCode.SUCCESS