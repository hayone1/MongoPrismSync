'''This module provides the cli'''

from typing import Optional
from kink import inject, di
import typer
from mongocd.Domain.Exceptions import SUCCESS, ERRORS
from mongocd import __app_name__, __version__
from mongocd.Core import config as prism_config
from logging import Logger
from mongocd.Interfaces.Services import *
from rich import print

app = typer.Typer()
logger = di[Logger]
mongoMigration = di[MongoMigration]
verifyService = di[IVerifyService]

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()
    
@app.command()
def init(
    config_folder_path: Optional[str] = typer.Option(
        os.getenv(Constants.config_folder_key, "MongoMigrate"),
        "--outputfolder",
        "-o",
        help="The folder to place the config file"
    ),
    sanitize_config: Optional[bool] = typer.Option(
        False,
        "--sanitize_config",
        "-s",
        help="""Weather or not the config yaml should be cleaned up.
        This will remove unnecessary fields"""
    ),
    update_templates: Optional[bool] = typer.Option(
        True,
        "--update_templates",
        "-u",
        help="""Weather or not to download the templates.
        This will overwrite existing templates with the same name."""
    ),
    template_url: Optional[str] = typer.Option(
        "https://github.com/hayone1/MongoPrismSync/releases/download/v1alpha1_v0.0.1/templates_v1alpha1.zip",
        "--template_url",
        "-t",
        help="""The url to download the template from. It is only
        effective if config file doesnt yet exist or sanitize_config is set to true"""
    )
) -> None:
    '''Initialize the application configurations and verify that the source database is reacheable'''
    logger.info("Starting: mongocd init")
    if prism_config.init_app(config_folder_path, sanitize_config, update_templates, template_url) != SUCCESS:
        raise typer.Exit(ReturnCodes.UNINITIALIZED.value)

@app.command()
def weave(
    config_folder_path: Optional[str] = typer.Option(
        os.getenv(Constants.config_folder_key, None),
        "--outputfolder",
        "-o",
        help="The folder to place the config file"
    ),
    source_password: Optional[str] = typer.Option(
        os.getenv(Constants.mongo_source_pass, None),
        "--source_password",
        "-p",
        help="Password of the source database"
    )
):
    #if any of the verifications did not succeed
    if any([verifyService.verify_connectivity(source_password).value, 
        verifyService.verify_databases().value]):
        raise typer.Exit(ReturnCodes.UNINITIALIZED.value)
    print("[green] Successfully connected to database")
    #VerifyDatabases
    
    
@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the cli version and exit.",
        callback=_version_callback,
        is_eager=True
    )
) -> None:
    return