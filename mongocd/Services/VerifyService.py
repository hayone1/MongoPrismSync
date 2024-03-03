
from kink import inject
from mongocd.Domain.Database import *
from mongocd.Interfaces.Services import IVerifyService



# @inject(alias=IVerifyService)
@inject
class VerifyService(IVerifyService):
    def __init__(self, mongoMigration: MongoMigration, clients: dict[str, DbClients], logger: Logger):
            self.logger = logger
            self.mongoMigration = mongoMigration
            self.clients = clients

    def VerifyConnectivity(self) -> bool:
        if (self.mongoMigration.secretVars['stringData'].get('source_password') == None):
            self.logger.error("unable to find key source_password in secret definition")
            return False
        source_password = self.mongoMigration.secretVars['stringData']['source_password']
        # destination_password = self.mongoMigration.secretVars['destination_password']

        self.logger.info("verify mongodb connectivity")
        for _databaseConfig in self.mongoMigration.databaseConfig[0:]:
            self.clients[_databaseConfig.name] = DbClients(
                    pyclient=MongoClient(self.mongoMigration.source_conn_string, password=source_password, authSource=_databaseConfig.source_authdb)[_databaseConfig.source_db],
                    shclient=f'mongosh "{self.mongoMigration.source_conn_string}" --password {source_password} --authenticationDatabase {_databaseConfig.source_authdb} --quiet --json=canonical',
                    shclientAsync=['mongosh', self.mongoMigration.source_conn_string, '--password', source_password, '--authenticationDatabase', _databaseConfig.source_authdb, '--quiet', '--json=canonical']) 
                    # f'mongosh "{self.mongoMigration.source_conn_string}" --password {source_password} --authenticationDatabase {_databaseConfig.source_authdb}')
            pymongoCheck = self.clients[_databaseConfig.name].pyclient.command('ping')
            mongoshCheck = self.clients[_databaseConfig.name].ShCommand("db.runCommand({ ping: 1 });")
            # print(pymongoCheck)
            # print(mongoshCheck)
            if (pymongoCheck['ok'] < 1 or mongoshCheck['ok']['$numberInt'] != '1'):
                self.logger.error("Connectivity test failed, program cannot continue")
                return False
            # print(f"source: {_databaseConfig.destination_db}", self.clients[_databaseConfig.name].destination_client[_databaseConfig.destination_db].command('ping'))
            
        self.logger.info("Successfully connected to source mongodb")
        return True

    @inject
    def VerifyDatabases(self) -> bool:
        self.logger.info("verify databases connectivity")
        databaseConfig = self.mongoMigration.spec.databaseConfig
        for _databaseConfig in databaseConfig:
            if _databaseConfig.skip == True:
                self.logger.warning(f"[{_databaseConfig.name}]: skip set to true, skipping...")
                continue
            source_db = self.clients[_databaseConfig.name].pyclient
            # destination_db = self.clients[_databaseConfig.name].source_client[_databaseConfig.destination_db]
            _databaseConfig.SetCollectionConfig(source_db)

            # _databaseConfig.collections_config.properties collection_names
        self.logger.info("successfully verified databases connectivity")
        return True
        # destination_collections = source_db.list_collection_names(filter=filter)
