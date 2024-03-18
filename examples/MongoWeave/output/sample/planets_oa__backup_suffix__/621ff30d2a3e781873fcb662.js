
var dbName = 'dample_dest';
var collName = 'planets_oa__backup_suffix__';
//comparison function will be added from another file
var sourceDataJson = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb662"
  },
  "name": "Venus",
  "orderFromSun": 2,
  "hasRings": false,
  "mainAtmosphere": [
    "CO2",
    "N"
  ],
  "surfaceTemperatureC": {
    "min": null,
    "max": null,
    "mean": 464
  }
};
var uniqueFields = {
  "_id": {
    "$oid": "621ff30d2a3e781873fcb662"
  }
};
db = db.getSiblingDB(dbName);
Comparison(dbName, collName, sourceDataJson, uniqueFields);



