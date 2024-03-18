
var dbName = 'dample_dest';
var collName = 'planets_oa';
//comparison function will be added from another file
var sourceDataJson = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb65e"
  },
  "name": "Mars",
  "orderFromSun": 4,
  "hasRings": false,
  "mainAtmosphere": [
    "CO2",
    "Ar",
    "N"
  ],
  "surfaceTemperatureC": {
    "min": -143,
    "max": 35,
    "mean": -63
  }
};
var uniqueFields = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb65e"
  }
};
db = db.getSiblingDB(dbName);
Comparison(dbName, collName, sourceDataJson, uniqueFields);



