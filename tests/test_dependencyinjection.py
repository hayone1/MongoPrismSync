from logging import Logger
import pytest
from typer.testing import CliRunner
from mongocd import __app_name__, __version__, cli
from kink import di

from mongocd.Domain.Database import DbClients, MongoMigration
from mongocd.Services.VerifyService import VerifyService

def test_di_content(runner: CliRunner):
    '''Test that dependencies are correctly injected'''
    result = runner.invoke(cli.app, ["--version"])
    assert isinstance(di[MongoMigration], MongoMigration | None)
    assert isinstance(di["clients"], dict | None)
    assert isinstance(di[VerifyService], VerifyService | None)
    assert isinstance(di[Logger], Logger)