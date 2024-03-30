from logging import Logger
import pytest
from kink import di

from mongocd.Domain.MongoMigration import MongoMigration
from mongocd.Services.VerifyService import VerifyService
from mongocd.Core import config

pytestmark = pytest.mark.skip("all tests still WIP")
def test_di_content():
    """Test that dependencies are correctly injected"""
    # result = runner.invoke(cli.app, ["--version"])
    config.inject_dependencies()
    assert isinstance(di[MongoMigration], MongoMigration | None)
    assert isinstance(di["clients"], dict | None)
    assert isinstance(di[VerifyService], VerifyService | None)
    assert isinstance(di[Logger], Logger)
#ToDo
# def test_di_response_no_connectivity(disable_network, caplog):
#     '''Test that a critical error is logged when there is no network connectivity
#         To the endpoints that need to be called'''
#     with caplog.at_level(logging.CRITICAL):
#         config.inject_dependencies()
#         print ("message",caplog.messages)
#         assert any("ReturnCode" in message for message in caplog.messages), "Expected critical error was not logged"
