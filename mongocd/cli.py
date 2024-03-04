'''This module provides the cli'''

from typing import Optional
from kink import inject, di
import typer
from mongocd.Domain.Exceptions import SUCCESS, ERRORS
from mongocd import __app_name__, __version__
from mongocd.Core import config as prism_config
from logging import Logger
from mongocd.Interfaces.Services import *

app = typer.Typer()
logger = di[Logger]
mongoMigration = di[MongoMigration]
verifyService = di[IVerifyService]

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()
    
@inject
@app.command()
def init(
    config_folder_path: Optional[str] = typer.Option(
        "MongoMigrate",
        "--outputfolder",
        "-o",
        help="The folder to place the config file"
    ),
    source_password: Optional[str] = typer.Option(
        "replace_with_password",
        "--source_password",
        "-p"
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
        effective if config file doesnt exist or sanitize_config is set to true"""
    )
) -> None:
    '''Initialize the application configurations and verify that the source database is reacheable'''
    logger.info("Starting: mongocd init")
    if prism_config.init_app(config_folder_path, source_password, sanitize_config, update_templates, template_url) != SUCCESS:
        raise typer.Exit(1)

@inject    
@app.command()
# cant use IVerifyService and MongoMigration here as they are meant
# to be cli argument, use di depedency ijection above
def weave(
    #Database verification
):
    verifyService.VerifyConnectivity()
    verifyService.VerifyDatabases()
    #VerifyDatabases
    
    
@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Shoe the cli version and exit.",
        callback=_version_callback,
        is_eager=True
    )
) -> None:
    return