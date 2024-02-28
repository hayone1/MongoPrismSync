
var newData = __newData__;
var fields = __fields__;
var dbName = '___dbName___';
var collName = '___collName___';

var newDataDecoded = EJSON.deserialize(newData);
var fieldsDecoded = EJSON.deserialize(fields);
db = db.getSiblingDB(dbName);
db.getCollection(collName).replaceOne(fieldsDecoded, newDataDecoded, {upsert: true});
       
       