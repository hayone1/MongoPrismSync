
var dbName = '{{ db_name }}';
var collName = '{{ coll_name }}';
// This is/are the index Field(s) that can be used to uniquely identify a document
var uniqueIndexFields = {{ unique_index_fields }};  // Replace with your actual index name

//generate dictionary from the keys
var indexKeys = {};
// Object.keys(indexInfo).forEach(key => {
uniqueIndexFields.forEach(key => {
    indexKeys[key] = "$" + key
});
//get the data
var data = db.getSiblingDB(dbName)[collName].aggregate([
    {
        $project: {
            _id: 0,
            "database": dbName,
            "collection": collName,
            "key" : indexKeys,
            "value": "$$ROOT"
        }
    }
]);
//final data
result = data.map(function (dt) {dt["filename"] = Object.values(dt["key"]).join("|"); return dt} );
//printjson(result);
// EJSON.serialize(result.toArray());
EJSON.stringify(result.toArray());