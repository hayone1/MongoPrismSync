'''Top-Level packages'''


       
    
# mongoMigration: MongoMigration = MongoMigration()
# connectivityRetry = lambda x: mongoMigration.spec.connectivityRetry
# # secretVars: dict[str,str]
# destination_client: MongoClient = MongoClient()
# clients: dict[str, DbClients] = dict()

from mongocd.Core.config import *
inject_dependencies()