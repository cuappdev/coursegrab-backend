from . import *


class UpdateSessionController(AppDevController):
    def get_path(self):
        return "/session/update/"

    def get_methods(self):
        return ["POST"]

    @extract_bearer
    def content(self, **kwargs):
        update_token = kwargs.get("bearer_token")
        session = sessions_dao.refresh_session(update_token)
        return session.serialize_session()
