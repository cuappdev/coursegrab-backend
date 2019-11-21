import abc


class BaseController:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_path(self):  # URI-path that begins and ends with a '/'
        return ""

    @abc.abstractmethod
    def get_methods(self):  # List of different HTTP methods supported
        return []

    @abc.abstractmethod
    def response(self, **kwargs):
        return None
