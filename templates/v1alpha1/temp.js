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