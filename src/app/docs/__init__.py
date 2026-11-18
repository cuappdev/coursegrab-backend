from os import path

from flask import Blueprint, render_template, send_from_directory


docs = Blueprint("docs", __name__, url_prefix="/docs", template_folder="templates")


@docs.route("/")
def swagger_ui():
    return render_template("swagger.html", spec_version=path.getmtime(path.join(docs.root_path, "openapi.json")))


@docs.route("/openapi.json")
def openapi_spec():
    return send_from_directory(docs.root_path, "openapi.json", cache_timeout=0)
