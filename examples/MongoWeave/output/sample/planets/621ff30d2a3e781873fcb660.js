
var dbName = 'dample_dest';
var collName = 'planets';
//comparison function will be added from another file
var sourceDataJson = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb660"
  },
  "name": "Jupiter",
  "orderFromSun": 5,
  "hasRings": true,
  "mainAtmosphere": [
    "H2",
    "He",
    "CH4"
  ],
  "surfaceTemperatureC": {
    "min": null,
    "max": null,
    "mean": -145.15
  }
};
var uniqueFields = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb660"
  }
};
db = db.getSiblingDB(dbName);
Comparison(dbName, collName, sourceDataJson, uniqueFields);



