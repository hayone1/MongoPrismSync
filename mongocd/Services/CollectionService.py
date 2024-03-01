from mongocd.Domain.Database import MongoMigration
from mongocd.Services.Interfaces import ICollectionService
from mongocd import logger

class CollectionService(ICollectionService):

    def VerifyConnectivity(_mongoMigration: MongoMigration) -> bool:
        if (_mongoMigration.secretVars['stringData'].get('source_password') == None):
            logger.error("unable to find key source_password in secret definition")
            return False
        source_password = _mongoMigration.secretVars['stringData']['source_password']
        # destination_password = _mongoMigration.secretVars['destination_password']

        logger.info("verify mongodb connectivity")
        for _databaseConfig in _mongoMigration.databaseConfig[0:]:
            clients[_databaseConfig.name] = DbClients(
                    pyclient=MongoClient(_mongoMigration.source_conn_string, password=source_password, authSource=_databaseConfig.source_authdb)[_databaseConfig.source_db],
                    shclient=f'mongosh "{_mongoMigration.source_conn_string}" --password {source_password} --authenticationDatabase {_databaseConfig.source_authdb} --quiet --json=canonical',
                    shclientAsync=['mongosh', _mongoMigration.source_conn_string, '--password', source_password, '--authenticationDatabase', _databaseConfig.source_authdb, '--quiet', '--json=canonical']) 
                    # f'mongosh "{_mongoMigration.source_conn_string}" --password {source_password} --authenticationDatabase {_databaseConfig.source_authdb}')
            pymongoCheck = clients[_databaseConfig.name].pyclient.command('ping')
            mongoshCheck = clients[_databaseConfig.name].ShCommand("db.runCommand({ ping: 1 });")
            # print(pymongoCheck)
            # print(mongoshCheck)
            if (pymongoCheck['ok'] < 1 or mongoshCheck['ok']['$numberInt'] != '1'):
                logger.error("Connectivity test failed, program cannot continue")
                return False
            # print(f"source: {_databaseConfig.destination_db}", clients[_databaseConfig.name].destination_client[_databaseConfig.destination_db].command('ping'))
            
        logger.info("Successfully connected to source mongodb")
        return True

    def VerifyDatabases(databaseConfig: list[DatabaseConfig]):
        logger.info("verify databases connectivity")
        for _databaseConfig in databaseConfig:
            if _databaseConfig.skip == True:
                logger.warning(f"[{_databaseConfig.name}]: skip set to true, skipping...")
                continue
            source_db = clients[_databaseConfig.name].pyclient
            # destination_db = clients[_databaseConfig.name].source_client[_databaseConfig.destination_db]
            _databaseConfig.SetCollectionConfig(source_db)

            # _databaseConfig.collections_config.properties collection_names
        logger.info("successfully verified databases connectivity")
        # destination_collections = source_db.list_collection_names(filter=filter)


