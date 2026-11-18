from flask import Blueprint, render_template, send_from_directory


docs = Blueprint("docs", __name__, url_prefix="/docs", template_folder="templates")


@docs.route("/")
def swagger_ui():
    return render_template("swagger.html")


@docs.route("/openapi.json")
def openapi_spec():
    return send_from_directory(docs.root_path, "openapi.json")
