
var dbName = '___dbName___';
var collName = '___collName___';
var unique_index_fields = __unique_index_fields__;  // Replace with your actual index name

// Get information about the specified index
// var indexInfo = db.getSiblingDB(dbName)[collName].getIndexes().filter(function(index) {
//     return index.name === indexName;
// })[0].key;

//generate dictionary from the keys
var indexKeys = {};
// Object.keys(indexInfo).forEach(key => {
unique_index_fields.forEach(key => {
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
//final data
result = data.map(function (dt) {dt["filename"] = Object.values(dt["key"]).join("|"); return dt} );
//printjson(result);
// EJSON.serialize(result.toArray());
printjson(EJSON.stringify(result.toArray()));