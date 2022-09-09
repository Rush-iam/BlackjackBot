from sqlalchemy import Column, Integer, Unicode

from app.packages.postgres.metadata import BaseMetadata


class AdminModel(BaseMetadata):
    __tablename__ = 'admins'

    id: int = Column(Integer(), primary_key=True)
    email: str = Column(Unicode(), unique=True, nullable=False)
    password: str = Column(Unicode(), nullable=False)
