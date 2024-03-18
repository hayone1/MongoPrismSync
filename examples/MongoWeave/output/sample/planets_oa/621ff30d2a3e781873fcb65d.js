
var dbName = 'dample_dest';
var collName = 'planets_oa';
//comparison function will be added from another file
var sourceDataJson = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb65d"
  },
  "name": "Uranus",
  "orderFromSun": 7,
  "hasRings": true,
  "mainAtmosphere": [
    "H2",
    "He",
    "CH4"
  ],
  "surfaceTemperatureC": {
    "min": null,
    "max": null,
    "mean": -197.2
  }
};
var uniqueFields = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb65d"
  }
};
db = db.getSiblingDB(dbName);
Comparison(dbName, collName, sourceDataJson, uniqueFields);



