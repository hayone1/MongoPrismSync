import pytest
from typer.testing import CliRunner
from mongocd import __app_name__, __version__, cli

pytestmark = pytest.mark.skip("all tests still WIP")
# runner = CliRunner()
# @pytest.mark.skip(reason="skip")
def test_version(runner: CliRunner):
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout

@pytest.mark.skip(reason="skip")
def test_init(runner: CliRunner):
    result = runner.invoke(cli.app, 
        ["init", "-o", "MongoMigrate", "-p", "test_password", "-sc"])
    print("Result: ", result.stdout)
    assert result.exit_code == 0
    # print("Result: ", result.stderr)