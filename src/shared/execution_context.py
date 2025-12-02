import typer
from nhlpy import NHLClient


class ExecutionContext:
    _app_name = "nhlpredictor"
    _file_path_set = False
    
    def __new__(cls):
        if not getattr(cls, '_instance', None):
            cls._instance = super(type(ExecutionContext), cls).__new__(cls)
        return cls._instance

    @property
    def client(self):
        if getattr(self, '_client', None) is None:
            self._client = NHLClient()
        return self._client

    @property
    def is_playoffs(self):
        return self._is_playoffs

    @is_playoffs.setter
    def is_playoffs(self, value: bool):
        self._is_playoffs = value

    @property
    def allow_update(self):
        return self._allow_update

    @allow_update.setter
    def allow_update(self, value: bool):
        self._allow_update = value

    @property
    def file_path(self):
        if self._file_path is None:
            typer.get_app_dir(ExecutionContext._app_name)
        return self._file_path

    @file_path.setter
    def file_path(self, value: str):
        if ExecutionContext._file_path_set:
            # TODO: shouldn't use general excdeption
            raise Exception("File path already set.")
        self._file_path = value
        ExecutionContext._file_path_set = True