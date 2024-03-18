function flattenObjectOld(obj, parentKey = "") {
    let result = {};
  
    for (const key in obj) {
      const newKey = parentKey ? `${parentKey}.${key}` : key;
  
      if (typeof obj[key] === 'object' && !Array.isArray(obj[key]) && obj[key] !== null) {
        const nested = flattenObject(obj[key], newKey);
        result = { ...result, ...nested };
      } else if (Array.isArray(obj[key])) {
        if (obj[key].length > 0 && typeof obj[key][0] === 'object' && !Array.isArray(obj[key][0]) && obj[key][0] !== null) {
          for (let i = 0; i < obj[key].length; i++) {
            const arrayItemKey = `${newKey}.${i}`;
            const arrayItem = flattenObject(obj[key][i], arrayItemKey);
            result = { ...result, ...arrayItem };
          }
        } else {
          result[newKey] = obj[key];
        }
      } else {
        result[newKey] = obj[key];
      }
    }
  
    return result;
}

function flattenObject(obj, parentKey = "") {
  let result = {};

  for (const key in obj) {
    const newKey = parentKey ? `${parentKey}.${key}` : key;

    if (typeof obj[key] === 'object' && obj[key] !== null) {
      // if (Array.isArray(obj[key])) {
      //   obj[key].forEach((item, index) => {
      //     const arrayItemKey = `${newKey}.${index}`;
      //     const arrayItem = flattenObject(item, arrayItemKey);
      //     result = { ...result, ...arrayItem };
      //   });
      // };
      // else {
        const nested = flattenObject(obj[key], newKey);
        result = { ...result, ...nested };
      // }
    } else {
      result[newKey] = obj[key];
    }
  }

  return result;
}
  
// Function to check if keys and values are the same
function KeysAndValuesEqual(dbName, collName, obj1, obj2) {
  const keys1 = Object.keys(obj1).sort();
  const keys2 = Object.keys(obj2).sort();

  // Check if the sorted key arrays are equal
  if (JSON.stringify(keys1) !== JSON.stringify(keys2)) {
    printjson({"msg":"at least 1 difference found between source and existing document keys", "database": dbName, "collection": collName, "key": `${keys1}|${keys2}` })
    return false;
  }
  
  // Check if values for each key are the same
  for (const key of keys1) {
    if (obj1[key] !== obj2[key]) {
      printjson({"msg":"at least 1 difference found between source and existing document values", 
      "database": dbName, "collection": collName, "key": `${key}`, "value": `${obj1[key]}|${obj2[key]}`})
      return false;
    }
  }

  return true;
}

function Comparison(dbName, collName, sourceDataJson, fieldsJson){
  var sourceDataBson = EJSON.deserialize(sourceDataJson);
  var fieldsBson = EJSON.deserialize(fieldsJson);
  db = db.getSiblingDB(dbName)
  var ExistingBson = db.getCollection(collName).findOne(fieldsBson);

  if (ExistingBson == null) {
    printjson({"msg":"No document in destination database matches given fields. Creating...", "databse": dbName, "collection": collName})
    db.getCollection(collName).insertOne(sourceDataBson);
    return;
  }
  
  //else
  const destinationDataJson = EJSON.serialize(ExistingBson);
  // printjson(ExistingBson);
  const flattenedSourceDataJson= flattenObject(sourceDataJson);
  const flattenedDestinationDataJson = flattenObject(destinationDataJson);
  
  // Check if keys are the same
  if (KeysAndValuesEqual(dbName, collName, flattenedSourceDataJson, flattenedDestinationDataJson)){
    printjson({"msg":"source and destination keys and values are equal. skipping...", "databse": dbName, "collection": collName})
    return
  }
  // else
  printjson({"msg":"difference found between source and existing document, replacing existing with replaceOne", "database": dbName, "collection": collName})
  // print(flattenedSourceDataJson)
  // print(flattenedDestinationDataJson)
  db.getCollection(collName).replaceOne(fieldsBson, sourceDataBson, {upsert: true});
};db.runCommand({ ping: 1 });db.getSiblingDB('dample_dest').createCollection('planets');
db.getSiblingDB('dample_dest').createCollection('planets__backup_suffix__');
db.getSiblingDB('dample_dest').createCollection('planets_oa');
db.getSiblingDB('dample_dest').createCollection('planets_oa__backup_suffix__');

var dbName = 'dample_dest';
// var collName = '';
var sourceCollectionsIndices = ['{\n  "collName": "planets",\n  "indices": [\n    {\n      "v": 2,\n      "key": {\n        "_id": 1\n      },\n      "name": "_id_"\n    },\n    {\n      "v": 2,\n      "key": {\n        "name": 1\n      },\n      "name": "name"\n    }\n  ]\n}', '{\n  "collName": "planets__backup_suffix__",\n  "indices": [\n    {\n      "v": 2,\n      "key": {\n        "_id": 1\n      },\n      "name": "_id_"\n    },\n    {\n      "v": 2,\n      "key": {\n        "name": 1\n      },\n      "name": "name"\n    }\n  ]\n}', '{\n  "collName": "planets_oa",\n  "indices": [\n    {\n      "v": 2,\n      "key": {\n        "_id": 1\n      },\n      "name": "_id_"\n    }\n  ]\n}', '{\n  "collName": "planets_oa__backup_suffix__",\n  "indices": [\n    {\n      "v": 2,\n      "key": {\n        "_id": 1\n      },\n      "name": "_id_"\n    }\n  ]\n}'];

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
//========================================

var dbName = 'dample_dest';
const sourceCollections = ['planets', 'planets__backup_suffix__', 'planets_oa', 'planets_oa__backup_suffix__'];
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
db.runCommand({ ping: 1 });// Replace 'source_collection' with the name of the source collection
// and 'target_collection' with the name of the duplicated collection
var dbName = 'dample_dest';
const sourceCollections = ['planets', 'planets__backup_suffix__', 'planets_oa', 'planets_oa__backup_suffix__'];
const backupSuffix = '_cd_backup';

db = db.getSiblingDB(dbName);
sourceCollections.forEach(source_collection => {
    target_collection = `${source_collection}${backupSuffix}`;
    print(`deleting backup Collection '${target_collection}'.`);
    // Drop the duplicated collection
    db.getCollection(targetCollection).drop();
});

// print(`Duplicate collection '${targetCollection}' deleted.`);