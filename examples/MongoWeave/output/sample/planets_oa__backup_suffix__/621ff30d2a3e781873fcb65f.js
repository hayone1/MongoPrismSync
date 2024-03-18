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
};
var dbName = 'dample_dest';
var collName = 'planets_oa__backup_suffix__';
//comparison function will be added from another file
var sourceDataJson = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb65f"
  },
  "name": "Neptune",
  "orderFromSun": 8,
  "hasRings": true,
  "mainAtmosphere": [
    "H2",
    "He",
    "CH4"
  ],
  "surfaceTemperatureC": {
    "min": null,
    "max": null,
    "mean": -201
  }
};
var uniqueFields = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb65f"
  }
};
db = db.getSiblingDB(dbName);
Comparison(dbName, collName, sourceDataJson, uniqueFields);



