

from motor.motor_asyncio import AsyncIOMotorClient
from ...config.config import settings

class monngoManager:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.DATABASE_URL)
        self.db = self.client[settings.DATABASE_NAME]
        

