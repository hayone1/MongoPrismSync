//========================================

var dbName = '{{ db_name }}';
const sourceCollections = {{ source_collections }};
const backupSuffix = '_cd_backup';
//var targetCollections = sourceCollections.map((coll) => `${coll}__backupSuffix__`);


db = db.getSiblingDB(dbName);
sourceCollections.forEach(source_collection => {
    target_collection = `${source_collection}${backupSuffix}`;
    print(`duplicating Collection '${source_collection}' duplicated to '${target_collection}'.`);
    
    // Duplicate the collection by using aggregate and $out
    db.getCollection(source_collection).aggregate([
        { $match: {} }, // Match all documents in the source collection
        { $out: target_collection } // Create a new collection with the matched documents
    ]);
    
    //also copy the indices and their properties
    var source_indexes = db.getCollection(source_collection).getIndexes();
    source_indexes.forEach(function(index) {
        if (index.name !== '_id_') {
            delete index.v;
            delete index.ns;
            var key = index.key;
            delete index.key;
            var options = {};
            for (var option in index) {
                options[option] = index[option];
            }
            var formattedOptions = JSON.stringify(options).replace(/\"([^\"]+)\":/g, '\$1:');
            var parsedOptions = eval('(' + formattedOptions + ')');
            db.getCollection(target_collection).createIndex(key, parsedOptions);
        }
    });
    print(`Collection '${source_collection}' duplicated to '${target_collection}'.`);

});

