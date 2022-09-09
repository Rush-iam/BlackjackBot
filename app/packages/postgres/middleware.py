from typing import Awaitable, Callable

from aiohttp.web import Request
from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound
from aiohttp.web_middlewares import middleware
from aiohttp.web_response import StreamResponse
from psycopg import errors
from sqlalchemy.exc import IntegrityError, NoReferenceError, NoResultFound


@middleware
async def database_error_handling_middleware(
    request: Request, handler: Callable[[Request], Awaitable[StreamResponse]]
) -> StreamResponse:
    try:
        return await handler(request)
    except IntegrityError as exc:
        details = exc.args[0].split('\n')[-1]
        match errors.lookup(exc.orig.pgcode):
            case errors.UniqueViolation:
                raise HTTPConflict(text=details) from exc
            case errors.ForeignKeyViolation:
                raise HTTPNotFound(text=details) from exc
        raise
    except (NoReferenceError, NoResultFound) as exc:
        raise HTTPNotFound(text='\n'.join(exc.args)) from exc
