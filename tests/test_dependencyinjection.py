from logging import Logger
import logging
import pytest, socket
import requests
from typer.testing import CliRunner
from mongocd import cli
from kink import di

from mongocd.Domain.Database import DbClients, MongoMigration
from mongocd.Services.VerifyService import VerifyService
from mongocd.Core import config

def test_di_content(runner: CliRunner):
    '''Test that dependencies are correctly injected'''
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
#         assert any("ReturnCodes" in message for message in caplog.messages), "Expected critical error was not logged"
