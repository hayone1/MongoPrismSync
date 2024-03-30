// Replace 'source_collection' with the name of the source collection
// and 'target_collection' with the name of the duplicated collection
var dbName = '{{ db_name }}';
const sourceCollections = {{ source_collections }};
const backupSuffix = '_cd_backup';

db = db.getSiblingDB(dbName);
sourceCollections.forEach(source_collection => {
    target_collection = `${source_collection}${backupSuffix}`;
    print(`deleting backup Collection '${target_collection}'.`);
    // Drop the duplicated collection
    db.getCollection(targetCollection).drop();
});

// print(`Duplicate collection '${targetCollection}' deleted.`);
