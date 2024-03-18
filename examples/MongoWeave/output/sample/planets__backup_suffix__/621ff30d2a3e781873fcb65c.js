
var dbName = 'dample_dest';
var collName = 'planets__backup_suffix__';
//comparison function will be added from another file
var sourceDataJson = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb65c"
  },
  "name": "Mercury",
  "orderFromSun": 1,
  "hasRings": false,
  "mainAtmosphere": [],
  "surfaceTemperatureC": {
    "min": -173,
    "max": 427,
    "mean": 67
  }
};
var uniqueFields = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb65c"
  }
};
db = db.getSiblingDB(dbName);
Comparison(dbName, collName, sourceDataJson, uniqueFields);



