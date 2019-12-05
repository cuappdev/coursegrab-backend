from . import *


class UpdateSessionController(AppDevController):
    def get_path(self):
        return "/session/update/"

    def get_methods(self):
        return ["POST"]

    @extract_bearer
    def content(self, **kwargs):
        update_token = kwargs.get("bearer_token")
        user = users_dao.refresh_session(update_token)
        return {
            "session_token": user.session_token,
            "session_expiration": user.session_expiration,
            "update_token": user.update_token,
        }
