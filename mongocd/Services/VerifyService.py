
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

        print("Starting: verify mongodb connectivity")
        # errored_database_clients = []
        # success_database_clients = []
        try:
            for db, client in self.clients.items():
                with progress: 
                    pyclient_task = progress.add_task(description="verifying pyclient connectivity...", total=1)
                    pymongoCheck = client.pyclient.command('ping')

                    shclient_task = progress.add_task(description="verifying shclient connectivity...", total=1)
                    mongoshCheck = client.ShCommand("db.runCommand({ ping: 1 });")
                    
                    #the commands above will also print their own outcome, so no need to add it to below log
                    if (pymongoCheck['ok'] < 1 or mongoshCheck['ok']['$numberInt'] != '1'):
                        self.logger.error(f"""{ReturnCode.DB_ACCESS_ERROR}: Failed connecting to database {source_conn_string} 
                                        | password: {source_password},
                                        Check that the details are correct and you have network access to the database.""")
                        return ReturnCode.DB_ACCESS_ERROR
                    utils.complete_richtask(pyclient_task, "py connectivity successful")
                    utils.complete_richtask(shclient_task, "sh connectivity successful")
        except Exception as ex:
            self.logger.error(f"""{ReturnCode.DB_ACCESS_ERROR}: Failed connecting to database {source_conn_string} 
                                | password: {source_password} | {ex}""")
            return ReturnCode.DB_ACCESS_ERROR

        print("Completed: verify mongodb connectivity")
        return ReturnCode.SUCCESS

    def verify_databases(self) -> ReturnCode:
        databaseConfigs = self.mongoMigration.spec.databaseConfigs
        progress = self.progress
        #list of databases that had connectivity issues
        errored_databases = []
        success_databases = []
        print("Starting: verify database")
        with progress:
            for databaseConfig in databaseConfigs:
                self.logger.debug(f"verify databases connectivity: {databaseConfig.name}")

                if self.clients == None:
                    self.logger.error("Pre-requisites not met to verify database. Please fill in correct details in the weaveconfig.yml")
                    return ReturnCode.INVALID_CONFIG_ERROR
                if databaseConfig.skip == True:
                    print(f"[yellow]-[/yellow] Skipping: {databaseConfig.name}")
                    continue

                database_verify_task = progress.add_task(description=f"verifying database: {databaseConfig.source_db}", total=None)
                source_db = self.clients[databaseConfig.name].pyclient
                # destination_db = self.clients[databaseConfig.name].source_client[databaseConfig.destination_db]
                if databaseConfig.SetCollectionConfig(source_db) != ReturnCode.SUCCESS:
                    errored_databases.append(databaseConfig.name)
                    utils.fault_richtask(database_verify_task, f"failed to verify database: {databaseConfig.source_db}")
                    continue
                success_databases.append(databaseConfig.name)
                utils.complete_richtask(database_verify_task, f"verified database: {databaseConfig.source_db}")
        
        if len(errored_databases) > 0:
            self.logger.warn(f"databases with connection errors: {errored_databases}")
        if len(success_databases) == 0:
            return ReturnCode.DB_ACCESS_ERROR
        
        self.logger.debug(f"successfully connected to some or all databases: {success_databases}")
        print("Completed: verify mongodb connectivity")
        return ReturnCode.SUCCESS
        
        
        # destination_collections = source_db.list_collection_names(filter=filter)
