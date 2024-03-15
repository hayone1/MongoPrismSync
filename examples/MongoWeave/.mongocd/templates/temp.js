//db.getCollection("TMF_fileDocument.files").find({"filename":"MicrosoftTeams-image (2)"})
var dbName = 'Dom_uat';
var collName = 'TMF_fileDocument.files';
var indexName = 'filename_1_uploadDate_1';  // Replace with your actual index name

// Get information about the specified index
var indexInfo = db.getSiblingDB(dbName)[collName].getIndexes().filter(function(index) {
    return index.name === indexName;
})[0].key;

//generate dictionary from the keys
var indexKeys = {};
Object.keys(indexInfo).forEach(key => {
    indexKeys[key] = "$" + key
});
//get the data
var data = db.getSiblingDB(dbName)[collName].aggregate([
    {
        $project: {
            _id: 0,
            "key" : indexKeys,
            "value": "$$ROOT"
        }
    }
]);
//remove spaces and symbols from filename to avoid naming errors
result = data.map(function (dt) {dt["filename"] = Object.values(dt["key"])
    .join().replace(/\s/g, '').replace(/[^a-zA-Z0-9]/g, ''); return dt} );
//printjson(result);
EJSON.serialize(result.toArray());


//========================================
//db.getCollection("planets").find({})

// Replace 'source_collection' with the name of the source collection
// and 'target_collection' with the desired name for the duplicate collection
var dbName = 'sample_guides';
const sourceCollections = ["planets","planets_oa"];
//var targetCollections = sourceCollections.map((coll) => `${coll}__backup_suffix__`);


db = db.getSiblingDB(dbName);
sourceCollections.forEach(source_collection => {
    target_collection = `${source_collection}__backup_suffix__`;
    print("Creating duplicate collection: " + target_collection)
    
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
});


