from .database import AsyncSessionType, Database


class DatabaseAccessor:
    def __init__(self, db: Database):
        self._db: Database = db

    def session(self) -> AsyncSessionType:
        return self._db.session()
