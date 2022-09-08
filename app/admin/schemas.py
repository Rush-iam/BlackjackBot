from marshmallow import fields

from app.web.base.base_schema import BaseSchema


class AdminSchema(BaseSchema):
    id = fields.Int(required=False)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class AdminLoginSchema(AdminSchema):
    class Meta:
        exclude = ('id',)
