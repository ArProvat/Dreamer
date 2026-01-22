

from motor.motor_asyncio import AsyncIOMotorClient
from ...config.config import settings
from ..mongoDB.monogoDB_schema import StorylineModel

class monngoManager:
    async def __init__(self):
        self.client = AsyncIOMotorClient(settings.DATABASE_URL)
        self.db = self.client[settings.DATABASE_NAME]
        self.book_collection = self.db['books']
        self.book_overview_collection = self.db['book_overviews']
        await self.create_index()
    
    async def create_index(self):
        await self.book_collection.create_index('book_id')
        await self.book_collection.create_index('user_id')
        await self.book_collection.create_index([('user_id',1),('book_id',1)])
        await self.book_collection.create_index([('book_id',1),('genre',1)])

    async def insert_story_overview(self,Storyline_data:dict):
        try:
            Storyline = StorylineModel(**Storyline_data)
            result = self.book_overview_collection.insert_one(Storyline.model_dump(by_alise=True))
            result.id = str(result.inserted_id)

        except Exception as e:
            raise e
    


    



        

