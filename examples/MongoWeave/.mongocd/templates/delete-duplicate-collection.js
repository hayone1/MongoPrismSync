// Replace 'source_collection' with the name of the source collection
// and 'target_collection' with the name of the duplicated collection
var dbName = '___dbName___';
var sourceCollection = '__sourceCollection__';
var targetCollection = `${sourceCollection}__backup_suffix__`;

db = db.getSiblingDB(dbName);

// Drop the duplicated collection
db.getCollection(targetCollection).drop();

print(`Duplicated collection '${targetCollection}' deleted.`);
