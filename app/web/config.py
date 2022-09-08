import os
from pathlib import Path
from typing import Annotated, Optional

from pydantic import (
    BaseModel,
    BaseSettings,
    ConstrainedStr,
    EmailStr,
    Field,
    PositiveInt,
    constr,
)
from sqlalchemy.engine.url import URL

from .logger import logger


DEFAULT_CONFIG_FILE = os.getenv('CONFIG_FILE', 'config.env')


class AtLeastOneCharStr(ConstrainedStr):
    min_length = 1
    strip_whitespace = True


class AppConfig(BaseModel):
    cookie_secret_key: Annotated[str, constr(min_length=32, max_length=32)]


class AdminConfig(BaseModel):
    email: EmailStr
    password: AtLeastOneCharStr


class BotConfig(BaseModel):
    token: AtLeastOneCharStr


class DatabaseConfig(BaseModel):
    drivername: str = 'postgresql+asyncpg'
    host: str = 'localhost'
    port: PositiveInt = 5432
    username: AtLeastOneCharStr
    password: str
    database: AtLeastOneCharStr = Field(..., alias='name')


class Config(BaseSettings):
    """
    Хранилище конфигурации, формируемой и переназначаемой из трёх источников:

    1) Параметры "по умолчанию" (переменные класса)
    2) Параметры из файла ``config.env`` (или ``CONFIG_FILE``)
    3) Параметры из переменных среды (высший приоритет)
        Для вложенных переменных используется разделитель ``__``
        Пример: admin.email -> ADMIN__EMAIL (регистр не важен)
    """

    app: AppConfig
    admin: AdminConfig
    bot: BotConfig
    database: DatabaseConfig

    class Config:
        env_nested_delimiter = '__'

    @property
    def database_dsn(self) -> str:
        return str(URL.create(**self.database.dict()))

    @property
    def database_dsn_sync(self) -> str:
        database_config = self.database.dict()
        database_config['drivername'] = 'postgresql'
        return str(URL.create(**database_config))


def get_config(config_path: Optional[str] = None) -> Config:
    if not config_path:
        config_path = DEFAULT_CONFIG_FILE

    try:
        Path(config_path).resolve(strict=True)
    except FileNotFoundError as exc:
        logger.warning('setup_config: config file %s does not exists', exc.filename)

    return Config(_env_file=config_path)  # type: ignore
