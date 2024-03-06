
from kink import inject
from mongocd.Domain.Base import *
from mongocd.Domain.Database import *
from mongocd.Interfaces.Services import IVerifyService
from rich import print


# @inject(alias=IVerifyService)
@inject
class VerifyService(IVerifyService):
    # parameters are injected by di
    def __init__(self, mongoMigration: MongoMigration, clients: dict[str, DbClients], logger: Logger):
            self.logger = logger
            self.mongoMigration = mongoMigration
            self.clients = clients

    def verify_connectivity(self, source_password: str) -> ReturnCodes:
        source_conn_string = self.mongoMigration.spec.source_conn_string

        if (source_password == None):
            self.logger.error(f"{Messages.envvar_inaccessible}: {Constants.mongo_source_pass}")
            return ReturnCodes.ENVVAR_ACCESS_ERROR
        
        if (utils.is_empty_or_whitespace(source_conn_string)):
            #source_conn_string= will print the variable name and value
            self.logger.error(f"{Messages.specvalue_missing}: {source_conn_string=}")
            return ReturnCodes.READ_CONFIG_ERROR
        # source_password = self.mongoMigration.spec.secretVars['stringData']['source_password']
        # destination_password = self.mongoMigration.spec.secretVars['destination_password']

        self.logger.info("verify mongodb connectivity")
        for _databaseConfig in self.mongoMigration.spec.databaseConfig[0:]:
            self.clients[_databaseConfig.name] = DbClients(
                    pyclient=MongoClient(source_conn_string, password=source_password, authSource=_databaseConfig.source_authdb)[_databaseConfig.source_db],
                    shclient=f'mongosh "{source_conn_string}" --password {source_password} --authenticationDatabase {_databaseConfig.source_authdb} --quiet --json=canonical',
                    shclientAsync=['mongosh', source_conn_string, '--password', source_password, '--authenticationDatabase', _databaseConfig.source_authdb, '--quiet', '--json=canonical']) 
                    # f'mongosh "{source_conn_string}" --password {source_password} --authenticationDatabase {_databaseConfig.source_authdb}')
            pymongoCheck = self.clients[_databaseConfig.name].pyclient.command('ping')
            mongoshCheck = self.clients[_databaseConfig.name].ShCommand("db.runCommand({ ping: 1 });")
            # print(pymongoCheck)
            # print(mongoshCheck)
            if (pymongoCheck['ok'] < 1 or mongoshCheck['ok']['$numberInt'] != '1'):
                self.logger.error(f"{ReturnCodes.DB_ACCESS_ERROR}: Failed connecting to database {source_conn_string}, Check that the details are correct and you have network access to the database.")
                return ReturnCodes.DB_ACCESS_ERROR
            # print(f"source: {_databaseConfig.destination_db}", self.clients[_databaseConfig.name].destination_client[_databaseConfig.destination_db].command('ping'))
            
        self.logger.info("Successfully connected to source mongodb")
        return ReturnCodes.SUCCESS

    def verify_databases(self) -> ReturnCodes:
        databaseConfig = self.mongoMigration.spec.databaseConfig

        #list of databases that had connectivity issues
        errored_databases = []
        success_databases = []
        for _databaseConfig in databaseConfig:
            self.logger.info(f"verify databases connectivity: {_databaseConfig.name}")
            if self.clients == None:
                print("[red] Pre-requisites not met to verify database. Please fill in correct details in the weaveconfig.yml")
                return ReturnCodes.INVALID_CONFIG_ERROR
            if _databaseConfig.skip == True:
                self.logger.warning(f"[{_databaseConfig.name}]: skip set to true, skipping...")
                continue
            source_db = self.clients[_databaseConfig.name].pyclient
            # destination_db = self.clients[_databaseConfig.name].source_client[_databaseConfig.destination_db]
            if _databaseConfig.SetCollectionConfig(source_db) != ReturnCodes.SUCCESS:
                errored_databases.append(_databaseConfig.name)
                continue
            # _databaseConfig.collections_config.properties collection_names
        if len(errored_databases) > 0:
            self.logger.warn(f"databases with connection errors: {errored_databases}")
        
        if len(success_databases) > 0:
            self.logger.info(f"successfully connected to some or all databases: {success_databases}")
            return ReturnCodes.SUCCESS
        else:
            return ReturnCodes.DB_ACCESS_ERROR
        # destination_collections = source_db.list_collection_names(filter=filter)
