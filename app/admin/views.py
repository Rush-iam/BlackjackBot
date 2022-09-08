from aiohttp.web_exceptions import HTTPForbidden
from aiohttp.web_response import json_response
from aiohttp_apispec import docs, json_schema, response_schema
from aiohttp_session import new_session

from app.web.base.base_view import AppView, AuthView
from app.web.logger import logger

from .dtos import Admin
from .schemas import AdminLoginSchema, AdminSchema


class AdminLoginView(AppView):
    @docs(
        tags=['admin'],
        summary='Admin login',
        description='Admin authorization by email and password',
    )
    @json_schema(AdminLoginSchema)
    @response_schema(AdminSchema)
    async def post(self):
        admin_request: Admin = Admin(**self.json)

        admin = await self.store.admins.get_by_email(admin_request.email)
        if not admin or not admin.is_password_matched_to(admin_request.password):
            raise HTTPForbidden

        session = await new_session(self.request)
        session['admin'] = admin.dict(exclude={'password'})
        logger.info('New Admin session: %s', admin.email)

        return json_response(AdminSchema().dump(admin))


class AdminCurrentView(AuthView):
    @docs(
        tags=['admin'],
        summary='Current admin',
        description='Shows current admin information',
    )
    @response_schema(AdminSchema)
    async def get(self):
        return json_response(AdminSchema().dump(self.request['admin']))
