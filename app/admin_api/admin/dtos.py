from hashlib import sha256

from pydantic import SecretStr

from app.admin_api.web.base.base_dto import DatabaseItem


class Admin(DatabaseItem):
    email: str
    password: SecretStr = SecretStr('')

    def is_password_matched_to(self, password: SecretStr) -> bool:
        password_hash = sha256(password.get_secret_value().encode()).hexdigest()
        return self.password.get_secret_value() == password_hash
