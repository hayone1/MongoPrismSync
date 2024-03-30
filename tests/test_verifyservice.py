import os
import pytest
from typer.testing import CliRunner
from mongocd import cli
from mongocd.Domain.Base import Constants, ReturnCode
from mongocd.Core import utils

from kink import di
from mongocd.Domain.MongoMigration import MongoMigration
from mongocd.Interfaces.Services import IVerifyService

pytestmark = pytest.mark.skip("all tests still WIP")
@pytest.fixture
def verifyService():
    return di[IVerifyService]
@pytest.fixture
def source_password():
    return os.getenv(Constants.MONGOSOURCEPASSWORD.name, None)
@pytest.fixture
def source_conn_string():
    if di[MongoMigration] is None: return None
    return di[MongoMigration].spec.source_conn_string

def test_verifyConnectivity_noPassword(verifyService, source_password, source_conn_string):
    '''Test that ReturnCode.ENVVAR_ACCESS_ERROR is returned by VerifyConnectivity when 
    source_password environment variable is not supplied'''
    if verifyService is None: return
    if (source_password is None):
        assert verifyService.verify_connectivity(source_password) == ReturnCode.ENVVAR_ACCESS_ERROR, \
        f"expected return code of {ReturnCode.ENVVAR_ACCESS_ERROR}, got: {verifyService.verify_connectivity(source_password)}"

def test_verifyConnectivity_noConnString(verifyService, source_password, source_conn_string):
    '''Test that {ReturnCode.READ_CONFIG_ERROR} is returned by VerifyConnectivity when 
    source_conn_string is not supplied in the weaveconfig yaml'''
    if verifyService is None: return
    if (source_password != None and utils.is_empty_or_whitespace(source_conn_string)):
        assert verifyService.verify_connectivity(source_password) == ReturnCode.READ_CONFIG_ERROR, \
        f"expected return code of {ReturnCode.READ_CONFIG_ERROR}, got: {verifyService.verify_connectivity(source_password)}"

def test_verify_connectivity(verifyService, source_password, source_conn_string):
    '''Test that when all parameters are supplied, {ReturnCode.SUCCESS} 
    or {ReturnCode.DB_ACCESS_ERROR} is returned by VerifyConnectivity'''
    if verifyService is None: return
    if source_password != None and not utils.is_empty_or_whitespace(source_conn_string):
        result = verifyService.verify_connectivity(source_password)
        assert result == ReturnCode.SUCCESS or result == ReturnCode.DB_ACCESS_ERROR, \
            f"expected {ReturnCode.SUCCESS} or {ReturnCode.DB_ACCESS_ERROR}. got {result}"
        
def test_verify_empty_databaseConfig(verifyService):
    '''Test that when {databaseConfig} is empty, {ReturnCode.DB_ACCESS_ERROR}
    is returned by VerifyDatabases'''
    if verifyService is None: return
    di[MongoMigration].spec.databaseConfigs = []
    result = verifyService.verify_databases()
    assert result == ReturnCode.DB_ACCESS_ERROR, \
            f"Expected {ReturnCode.DB_ACCESS_ERROR}, got {result}"