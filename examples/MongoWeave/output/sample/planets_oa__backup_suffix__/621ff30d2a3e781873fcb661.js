
var dbName = 'dample_dest';
var collName = 'planets_oa__backup_suffix__';
//comparison function will be added from another file
var sourceDataJson = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb661"
  },
  "name": "Earth",
  "orderFromSun": 3,
  "hasRings": false,
  "mainAtmosphere": [
    "N",
    "O2",
    "Ar"
  ],
  "surfaceTemperatureC": {
    "min": -89.2,
    "max": 56.7,
    "mean": 14
  }
};
var uniqueFields = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb661"
  }
};
db = db.getSiblingDB(dbName);
Comparison(dbName, collName, sourceDataJson, uniqueFields);



