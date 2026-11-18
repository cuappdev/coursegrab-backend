import re

from app import app


def test_docs_are_public_and_use_local_spec():
    with app.test_client() as client:
        response = client.get("/docs/")
        assert response.status_code == 200
        assert response.mimetype == "text/html"
        html = response.get_data(as_text=True)
        assert '"/docs/openapi/v1.json?v=' in html
        assert '"/docs/openapi/v2.json?v=' in html
        assert "persistAuthorization: false" in html
        assert "validatorUrl: null" in html
        assert client.get("/docs").status_code in (301, 308)
        spec_response = client.get("/docs/openapi.json")
        assert spec_response.status_code == 200
        assert spec_response.mimetype == "application/json"


def test_openapi_covers_every_api_route_and_method():
    with app.test_client() as client:
        spec = client.get("/docs/openapi.json").get_json()
    actual = {
        (re.sub(r"<(?:[^:<>]+:)?([^<>]+)>", r"{\1}", rule.rule), method.lower())
        for rule in app.url_map.iter_rules()
        if rule.endpoint.split(".")[0] in ("coursegrab", "coursegrab_v2")
        for method in rule.methods - {"HEAD", "OPTIONS"}
    }
    documented = {(path, method) for path, operations in spec["paths"].items() for method in operations}
    assert documented == actual
    operation_ids = [operation["operationId"] for operations in spec["paths"].values() for operation in operations.values()]
    assert len(operation_ids) == len(set(operation_ids))


def test_openapi_auth_contracts_and_references():
    with app.test_client() as client:
        spec = client.get("/docs/openapi.json").get_json()
    assert spec["servers"] == [{"url": "/", "description": "Server hosting these docs"}]
    for path, operations in spec["paths"].items():
        for operation in operations.values():
            if path.startswith("/api/v2/"):
                assert {"FirebaseAuth": []} in operation["security"]
            elif path == "/api/session/update/":
                assert operation["security"] == [{"LegacyRefresh": []}]
            elif path == "/api/session/initialize/" or path.startswith("/api/notification/"):
                assert operation["security"] == []
            else:
                assert {"LegacySession": []} in operation["security"]
            anonymous = path.endswith("/courses/search/") or path.endswith("/courses/{id}/")
            assert ({} in operation["security"]) == anonymous

    def check_references(value):
        if isinstance(value, dict):
            if "$ref" in value:
                assert value["$ref"].startswith("#/")
                target = spec
                for part in value["$ref"][2:].split("/"):
                    target = target[part]
            for child in value.values():
                check_references(child)
        elif isinstance(value, list):
            for child in value:
                check_references(child)

    check_references(spec)


def test_version_specs_partition_routes_and_credentials():
    with app.test_client() as client:
        full = client.get("/docs/openapi.json").get_json()
        v1 = client.get("/docs/openapi/v1.json").get_json()
        v2 = client.get("/docs/openapi/v2.json").get_json()
        assert client.get("/docs/openapi/v3.json").status_code == 404
    assert set(v1["paths"]) | set(v2["paths"]) == set(full["paths"])
    assert not set(v1["paths"]) & set(v2["paths"])
    assert all(route.startswith("/api/v2/") for route in v2["paths"])
    assert set(v1["components"]["securitySchemes"]) == {"LegacySession", "LegacyRefresh"}
    assert set(v2["components"]["securitySchemes"]) == {"FirebaseAuth"}
