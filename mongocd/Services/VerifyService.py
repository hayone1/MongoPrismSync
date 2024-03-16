
from kink import inject
from mongocd.Domain.Base import *
from mongocd.Domain.Database import *
from mongocd.Interfaces.Services import IVerifyService
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn


# @inject(alias=IVerifyService)
@inject
class VerifyService(IVerifyService):
    # parameters are injected by di
    def __init__(self, mongoMigration: MongoMigration, clients: dict[str, DbClients],
                logger: Logger = None, progress: Progress = None):
            self.logger = logger
            self.mongoMigration = mongoMigration
            self.clients = clients
            self.progress = progress

    def verify_connectivity(self, source_password: str) -> ReturnCode:
        source_conn_string = self.mongoMigration.spec.source_conn_string
        progress = self.progress
        if (source_password == None):
            self.logger.fatal(f"{ReturnCode.ENVVAR_ACCESS_ERROR}: {Messages.envvar_inaccessible}: {Constants.mongo_source_pass}")
            return ReturnCode.ENVVAR_ACCESS_ERROR
        
        if (utils.is_empty_or_whitespace(source_conn_string)):
            #source_conn_string= will print the variable name and value
            self.logger.fatal(f"{ReturnCode.READ_CONFIG_ERROR}: {Messages.specvalue_missing}: {source_conn_string=}")
            return ReturnCode.READ_CONFIG_ERROR
        # source_password = self.mongoMigration.spec.secretVars['stringData']['source_password']
        # destination_password = self.mongoMigration.spec.secretVars['destination_password']

        self.logger.info("verify mongodb connectivity")
        # errored_database_clients = []
        # success_database_clients = []
        for db, client in self.clients.items():
            try:
                pyclient_task = progress.add_task(description="verifying pyclient connectivity...", total=1)
                pymongoCheck = client.pyclient.command('ping')
                progress.update(pyclient_task, completed=True, description="[green]✓[/green]pyclient connectivity successful")

                shclient_task = progress.add_task(description="verifying shclient connectivity...", total=1)
                mongoshCheck = client.ShCommand("db.runCommand({ ping: 1 });")
                progress.update(shclient_task, completed=True, description="[green]✓[/green]pyclient connectivity successful")

                    
                # print(pymongoCheck)
                # print(mongoshCheck)
                #the commands above will also print their own outcome, so no need to add it to below log
                if (pymongoCheck['ok'] < 1 or mongoshCheck['ok']['$numberInt'] != '1'):
                    self.logger.error(f"""{ReturnCode.DB_ACCESS_ERROR}: Failed connecting to database {source_conn_string} 
                                      | password: {source_password},
                                      Check that the details are correct and you have network access to the database.""")
                    return ReturnCode.DB_ACCESS_ERROR
            except Exception as ex:
                    self.logger.error(f"""{ReturnCode.DB_ACCESS_ERROR}: Failed connecting to database {source_conn_string} 
                                      | password: {source_password} | {ex}""")
                    return ReturnCode.DB_ACCESS_ERROR

            # print(f"source: {databaseConfig.destination_db}", self.clients[databaseConfig.name].destination_client[databaseConfig.destination_db].command('ping'))
            
        self.logger.info("Successfully connected to source mongodb")
        return ReturnCode.SUCCESS

    def verify_databases(self) -> ReturnCode:
        databaseConfigs = self.mongoMigration.spec.databaseConfigs

        #list of databases that had connectivity issues
        errored_databases = []
        success_databases = []
        for databaseConfig in databaseConfigs:
            self.logger.info(f"verify databases connectivity: {databaseConfig.name}")
            if self.clients == None:
                print("[red] Pre-requisites not met to verify database. Please fill in correct details in the weaveconfig.yml")
                return ReturnCode.INVALID_CONFIG_ERROR
            if databaseConfig.skip == True:
                self.logger.warning(f"[{databaseConfig.name}]: skip set to true, skipping...")
                continue
            source_db = self.clients[databaseConfig.name].pyclient
            # destination_db = self.clients[databaseConfig.name].source_client[databaseConfig.destination_db]
            if databaseConfig.SetCollectionConfig(source_db) != ReturnCode.SUCCESS:
                errored_databases.append(databaseConfig.name)
                continue
            success_databases.append(databaseConfig.name)
            # databaseConfig.collections_config.properties collection_names
        if len(errored_databases) > 0:
            self.logger.warn(f"databases with connection errors: {errored_databases}")
        
        if len(success_databases) > 0:
            self.logger.info(f"successfully connected to some or all databases: {success_databases}")
            return ReturnCode.SUCCESS
        else:
            return ReturnCode.DB_ACCESS_ERROR
        # destination_collections = source_db.list_collection_names(filter=filter)
