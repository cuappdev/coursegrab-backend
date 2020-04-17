from . import *


class GetSectionController(AppDevController):
    def get_path(self):
        return "/sections/<catalog_num>/"

    def get_methods(self):
        return ["GET"]

    @authorize_user
    def content(self, **kwargs):
        user = kwargs.get("user")
        catalog_num = int(request.view_args["catalog_num"])
        section = sections_dao.get_section_by_catalog_num(catalog_num)
        return section.serialize_with_user(user.id)
