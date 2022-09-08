import json
from json import JSONDecodeError
from typing import Awaitable, Callable, Type, cast

from aiohttp.abc import AbstractView
from aiohttp.web import Request
from aiohttp.web_app import Application
from aiohttp.web_exceptions import HTTPException, HTTPUnauthorized
from aiohttp.web_middlewares import middleware
from aiohttp.web_response import StreamResponse, json_response
from aiohttp_apispec import validation_middleware
from aiohttp_session import get_session

from app.admin.dtos import Admin
from app.store.database.middleware import database_error_handling_middleware

from .base.base_view import AuthView


def setup_middlewares(app: Application) -> None:
    app.middlewares.extend(
        [
            error_handling_middleware,
            auth_middleware,
            validation_middleware,
            database_error_handling_middleware,
        ]
    )


@middleware
async def error_handling_middleware(
    request: Request, handler: Callable[[Request], Awaitable[StreamResponse]]
) -> StreamResponse:
    try:
        return await handler(request)
    except HTTPException as exc:
        try:
            reason = json.loads(str(exc.text))
        except JSONDecodeError:
            reason = exc.text
        return json_response(
            data={'message': exc.reason, 'reason': reason},
            status=exc.status,
        )


@middleware
async def auth_middleware(
    request: Request, handler: Callable[[Request], Awaitable[StreamResponse]]
) -> StreamResponse:
    handler_view = cast(Type[AbstractView], request.match_info.handler)
    if issubclass(handler_view, AuthView):
        session = await get_session(request)
        if not session:
            raise HTTPUnauthorized
        request['admin'] = Admin(**session['admin'])
    return await handler(request)
