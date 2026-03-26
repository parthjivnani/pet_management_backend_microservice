from motor.motor_asyncio import AsyncIOMotorClient
from core.config import configs


class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(configs.MONGODB_URI)
        self.db = self.client[configs.MONGODB_DB]
        self.pets = self.db["pets"]


_db: Database | None = None


def get_database() -> Database:
    global _db
    if _db is None:
        _db = Database()
    return _db
