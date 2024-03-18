
var dbName = 'dample_dest';
var collName = 'planets_oa__backup_suffix__';
//comparison function will be added from another file
var sourceDataJson = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb663"
  },
  "name": "Saturn",
  "orderFromSun": 6,
  "hasRings": true,
  "mainAtmosphere": [
    "H2",
    "He",
    "CH4"
  ],
  "surfaceTemperatureC": {
    "min": null,
    "max": null,
    "mean": -139.15
  }
};
var uniqueFields = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb663"
  }
};
db = db.getSiblingDB(dbName);
Comparison(dbName, collName, sourceDataJson, uniqueFields);



