
var dbName = '{{ db_name }}';
// var collName = '{{ coll_name }}';
var sourceCollectionsIndices = {{ source_collections_indices }};

var db = db.getSiblingDB(dbName);
sourceCollectionsIndices.forEach(function(sourceIndices) {
    var sourceIndicesBson = EJSON.deserialize(sourceIndices['indices']);
    var collName = sourceIndices['collName']
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

});

