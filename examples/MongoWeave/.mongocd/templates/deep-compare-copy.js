
var dbName = '___dbName___';
var collName = '___collName___';
//comparison function will be added from another file
var fieldsJson = __fieldsJson__;
var sourceDataJson = __sourceDataJson__;
db = db.getSiblingDB(dbName);
Comparison(dbName, collName, sourceDataJson, fieldsJson);




