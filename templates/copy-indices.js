
var dbName = '___dbName___';
var collName = '___collName___';
var sourceIndices = __sourceIndices__;

var sourceIndicesBson = EJSON.deserialize(sourceIndices);

db = db.getSiblingDB(dbName);
sourceIndicesBson.forEach(function(index) {
    if (index.name !== '_id_') {
        delete index.v;
        delete index.ns;
        var key = index.key;
        var indexExists = db.getCollection(collName).getIndexes().some(function(existingIndex) {
            return JSON.stringify(existingIndex.key) === JSON.stringify(key);
        });
        if (!indexExists) {
            delete index.key;
            var options = {};
            for (var option in index) {
                options[option] = index[option];
            }
            var formattedOptions = JSON.stringify(options).replace(/\"([^\"]+)\":/g, '\$1:');
            var parsedOptions = eval('(' + formattedOptions + ')');
            db.getCollection(collName).createIndex(key, parsedOptions);
        } else {
            print('Index with key ' + JSON.stringify(key) + ' already exists in target collection.');
        }
    }
});
