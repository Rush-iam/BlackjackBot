from aiohttp.web import run_app

from app.admin_api.web.app import create_app


app = create_app()

if __name__ == '__main__':
    run_app(app, access_log_format='%a "%r" %s %b "%{User-Agent}i"')
