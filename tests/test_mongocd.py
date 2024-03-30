import logging
import pytest
from typer.testing import CliRunner
from mongocd import cli
from mongocd.Core.config import __app_name__, __version__

pytestmark = pytest.mark.skip("all tests still WIP")
# runner = CliRunner()
# @pytest.mark.skip(reason="skip")
def test_version(runner: CliRunner):
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout

# @pytest.mark.skip(reason="skip")
def test_init(runner: CliRunner, caplog):
    result = runner.invoke(cli.app, 
        ["init", "-o", "MongoMigrate", "-s"])
    # print("Result: ", result.stdout)
    with caplog.at_level(logging.ERROR):
        assert result.exit_code == 0 or \
        any("ReturnCode" in message for message in caplog.messages), "Expected ERROR was not logged"

    # print("Result: ", result.stderr)

# def test_weave_verification
# def test_weave_no_connectivity(runner: CliRunner, caplog):
#     '''Test that a critical error is logged when there is no network connectivity
#         To the endpoints that need to be called'''
#     result = runner.invoke(cli.app, 
#     ["weave", "-o", "examples/MongoWeave" "-p", "irrelevant"])
#     assert result.exit_code == 0 
#     with caplog.at_level(logging.CRITICAL):
#         print("logs: ",caplog.messages)
#         assert any("ReturnCode" in message for message in caplog.messages), "Expected critical error was not logged"