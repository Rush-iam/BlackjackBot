from pydantic import BaseModel


class OrmItem(BaseModel):
    class Config:
        orm_mode = True


class DatabaseItem(OrmItem):
    id: int | None = None
