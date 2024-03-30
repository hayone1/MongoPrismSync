import pytest
from typer.testing import CliRunner

from mongocd.Domain.Database import DocumentData

@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def planet_mercury():
    return {
        "database": "sample_guides",
        "collection": "planets",
        "key": {"_id": {"$oid": "621ff30d2a3e781873fcb65c"}, "name": "Mercury"},
        "data": {
            "_id": {"$oid": "621ff30d2a3e781873fcb65c"},
            "name": "Mercury",
            "orderFromSun": 1,
            "hasRings": False,
            "mainAtmosphere": ["thin", "undetectable", "unhabitable"],
            "surfaceTemperatureC": {"min": -173, "max": 427, "mean": 67},
        },
        "filename": "621ff30d2a3e781873fcb65c|Mercury",
    }
@pytest.fixture
def planet_uranus():
    return {
        "database": "sample_guides",
        "collection": "planets",
        "key": {"_id": {"$oid": "621ff30d2a3e781873fcb65d"}, "name": "Uranus"},
        "data": {
        "_id": {
            "$oid": "621ff30d2a3e781873fcb65d"
        },
        "name": "Uranus",
        "orderFromSun": 6,
        "hasRings": False,
        "mainAtmosphere": [
            "H2",
            "He",
            "CH4"
        ],
        "surfaceTemperatureC": {
            "min": None,
            "max": None,
            "mean": -197.2
        }
        },
        "filename": "621ff30d2a3e781873fcb65c|Mercury",
    }

@pytest.fixture
def mercury_documentdata(planet_mercury) -> DocumentData:
    return DocumentData(**planet_mercury)
@pytest.fixture
def uranus_documentdata(planet_uranus) -> DocumentData:
    return DocumentData(**planet_uranus)