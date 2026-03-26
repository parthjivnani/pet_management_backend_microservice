from motor.motor_asyncio import AsyncIOMotorClient
from core.config import configs


class Database:
    """MongoDB connection using Motor (async)."""

    def __init__(self):
        self.client = AsyncIOMotorClient(configs.MONGODB_URI)
        self.db = self.client[configs.MONGODB_DB]
        self.users = self.db["users"]

    def get_collection(self, name: str):
        return self.db[name]


_db: Database | None = None


def get_database() -> Database:
    global _db
    if _db is None:
        _db = Database()
    return _db
