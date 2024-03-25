

from pydantic import BaseModel, ValidationInfo, field_validator

from mongocd.Domain.Base import CustomResource, Messages
from mongocd.Domain.Database import DatabaseConfig
from mongocd.Domain.PostRender import PostRenderer
from mongocd.Core import utils


class MongoMigrationSpec(BaseModel):
    secretVars: dict = dict()
    # dump_folder: str = "dump"
    source_conn_string: str = ""
    destination_conn_string: str = ""
    connectivityRetry: int = 5
    remote_template: str = "https://github.com/hayone1/MongoPrismSync/releases/download/v1alpha1_v0.0.1/templates_v1alpha1.zip"
    databaseConfigs: list[DatabaseConfig] = [DatabaseConfig()]
    postRenderers: dict[str, PostRenderer] = [PostRenderer()]
    # postRenderers: list[PostRenderer] = [PostRenderer()]

    @field_validator('source_conn_string', 'remote_template')
    @classmethod
    def check_string(cls, value: str, info: ValidationInfo):
        assert (not utils.is_empty_or_whitespace(value)), f"{info.field_name} {Messages.empty_notallowed}"
        assert ('//' in value), f"{info.field_name} must be valid uri"
        return value

    @field_validator('connectivityRetry')
    @classmethod
    def check_int(cls, value: str, info: ValidationInfo):
        assert value > 0, f"{info.field_name} must be a positive integer"
        return value


class MongoMigration(CustomResource):
    spec: MongoMigrationSpec = MongoMigrationSpec()

    #if config is coming from file
    #didnt use __init__ because i'm not sure if safe_load will 
    #call __init__ again
    # def Init(self: Self, config_file_path: str) -> Self:
    #     with open(config_file_path, 'r') as file:
    #         yaml_data: dict = yaml.safe_load(file)
    #         self = MongoMigration(**yaml_data)
    #         return self
   