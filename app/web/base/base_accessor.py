from aiohttp.web_app import Application


class BaseAccessor:
    def __init__(self, app: Application):
        self.app = app
        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    async def connect(self, app: Application) -> None:
        pass

    async def disconnect(self, app: Application) -> None:
        pass
