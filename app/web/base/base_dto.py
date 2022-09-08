from pydantic import BaseModel


class DatabaseItem(BaseModel):
    id: int | None = None

    class Config:
        orm_mode = True
