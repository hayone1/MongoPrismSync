
var dbName = 'dample_dest';
var collName = 'planets';
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



