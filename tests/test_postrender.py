

# apply method successfully applies patches to source_documents
from mongocd.Domain.PostRender import Kustomize, Patch


def test_Kustomize_apply_patches(mercury_documentdata, uranus_documentdata):
    """
    Test that the kustomize object is able to successfully
    apply patches
    """
    kustomize = Kustomize(patches=[
        Patch(
            target={
                "database": "sample_guides",
                "key": { "name": "Mercury"}
            },
            patch="""[
                {"op": "add", "path": "/habitable", "value": false},
                {"op": "add", "path": "/meta", "value": ["false_test"]},
                {"op": "remove", "path": "/orderFromSun"},
            ]
            """
            ),
        Patch(
            target={
                "database": "sample_guides",
                "key": { "name": "Uranus"}
            },
            patch="""
orderFromSun: 7
hasRings: true
            """
            ),
        Patch(
            target={
                "database": "sample_guides",
                "collection": "planets",
                "key": { "name": "Mercury"}
            },
            # replace should only work for Mercury as Uranus does
            # not satisfy the test
            patch="""[
                {"op": "test", "path": "/mainAtmosphere", "value": ["thin", "undetectable", "unhabitable"]},
                {"op": "remove", "path": "/mainAtmosphere/1"},
                {"op": "replace", "path": "/meta", "value": ["true_test"]},
            ]
            """
            ),
    ])

    source_documents = [mercury_documentdata,uranus_documentdata]

    # config_folder_path = "/path/to/config/folder"

    result_documents = list(kustomize.apply(source_documents))

    assert len(result_documents) == len(source_documents), \
        "length of result_documents and source_documents mismatch"
    for documentdata in result_documents:
        if "Mercury" in documentdata.key["name"]:
            assert documentdata.data["habitable"] is False
            assert "orderFromSun" not in documentdata.data
            assert len(documentdata.data["mainAtmosphere"]) == 2
            assert documentdata.data["meta"] == ["true_test"]
        if "Uranus" in documentdata.key["name"]:
            assert documentdata.data["orderFromSun"] == 7
            assert documentdata.data["hasRings"] is True