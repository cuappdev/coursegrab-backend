from app.coursegrab.utils.base_controller import abc, BaseController
from datetime import datetime
from flask import current_app, jsonify, request
from app.coursegrab.utils.api_error import APIError

# A REST-API controller that handles boilerplate for
# serving up JSON responses based on HTTP verbs
class AppDevController(BaseController):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def content(self, **kwargs):
        return dict()

    def get_name(self):
        return self.get_path().replace("/", "-")

    def response(self, **kwargs):
        try:
            content = self.content(**kwargs)
            return jsonify({"success": True, "data": content, "timestamp": round(datetime.now().timestamp())})
        except APIError as e:
            response = jsonify(
                {"success": False, "data": {"errors": [str(e)]}, "timestamp": round(datetime.now().timestamp())}
            )
            response.status_code = e.status_code
            if e.status_code == 401:
                response.headers["WWW-Authenticate"] = "Bearer"
            return response
        except Exception as e:
            if request.blueprint == "coursegrab_v2":
                current_app.logger.exception("Unhandled API failure")
                return jsonify(
                    {
                        "success": False,
                        "data": {"errors": ["Internal server error."]},
                        "timestamp": round(datetime.now().timestamp()),
                    }
                ), 500
            return jsonify(
                {"success": False, "data": {"errors": [str(e)]}, "timestamp": round(datetime.now().timestamp())}
            )
