import json
from os import path

from flask import Blueprint, abort, jsonify, render_template, send_from_directory


docs = Blueprint("docs", __name__, url_prefix="/docs", template_folder="templates")


@docs.route("/")
def swagger_ui():
    return render_template("swagger.html", spec_version=path.getmtime(path.join(docs.root_path, "openapi.json")))


@docs.route("/openapi.json")
def openapi_spec():
    return send_from_directory(docs.root_path, "openapi.json", cache_timeout=0)


@docs.route("/openapi/<version>.json")
def version_spec(version):
    if version not in ("v1", "v2"):
        abort(404)
    with open(path.join(docs.root_path, "openapi.json")) as spec_file:
        spec = json.load(spec_file)
    spec["paths"] = {
        route: operations for route, operations in spec["paths"].items()
        if route.startswith("/api/v2/") == (version == "v2")
    }
    categories = {tag for operations in spec["paths"].values() for operation in operations.values()
                  for tag in operation["tags"]}
    spec["tags"] = [tag for tag in spec["tags"] if tag["name"] in categories]
    spec["components"]["securitySchemes"] = {
        name: scheme for name, scheme in spec["components"]["securitySchemes"].items()
        if (name == "FirebaseAuth") == (version == "v2")
    }
    spec["info"]["title"] = "coursegrab-backend " + version.upper()
    spec["info"]["description"] = "API documentation for CourseGrab. Select an API version above and expand a category to browse endpoints."
    return jsonify(spec)
