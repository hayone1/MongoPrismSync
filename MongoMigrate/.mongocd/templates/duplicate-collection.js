// Replace 'source_collection' with the name of the source collection
// and 'target_collection' with the desired name for the duplicate collection
var dbName = '___dbName___';
var sourceCollection = '__sourceCollection__';
var targetCollection = `${sourceCollection}__backup_suffix__`;

db = db.getSiblingDB(dbName)
// Duplicate the collection by using aggregate and $out
db.getCollection(sourceCollection).aggregate([
    { $match: {} }, // Match all documents in the source collection
    { $out: targetCollection } // Create a new collection with the matched documents
]);

print(`Collection '${sourceCollection}' duplicated to '${targetCollection}'.`);
