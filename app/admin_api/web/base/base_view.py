from typing import Any

from aiohttp.web_urldispatcher import View

from app.admin_api.web.store import Store


class AppView(View):
    @property
    def json(self) -> dict[str, Any]:
        return self.request['json']

    @property
    def query(self) -> dict[str, Any]:
        return self.request['querystring']

    @property
    def store(self) -> Store:
        return self.request.app['store']


class AuthView(AppView):
    ...
