
var dbName = '{{ db_name }}';
var collName = '{{ coll_name }}';
//comparison function will be added from another file
var sourceDataJson = {{ source_data_json }};
var uniqueFields = {{ unique_fields }};
db = db.getSiblingDB(dbName);
Comparison(dbName, collName, sourceDataJson, uniqueFields);




