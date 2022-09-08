import json
from typing import Any

from aiohttp.web_exceptions import HTTPUnprocessableEntity
from marshmallow import Schema, ValidationError


class BaseSchema(Schema):
    def handle_error(self, error: ValidationError, data: Any, **kwargs: Any) -> None:
        raise HTTPUnprocessableEntity(text=json.dumps(error.messages))
