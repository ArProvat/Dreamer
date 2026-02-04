from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from ...config.config import settings

class MongoManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    async def initialize(self ):
        """Initialize the MongoDB connection"""
        if not self._initialized:
            self.client = AsyncIOMotorClient(settings.DATABASE_URL)
            self.db = self.client[settings.DATABASE_NAME]
            self.book_collection = self.db['Books']
            self.book_overview_collection = self.db['book_overviews']
            self.sessions = self.db["sessions"]
            await self.create_index()
            self._initialized = True
    
    async def create_index(self):
        """Create database indexes"""
        await self.book_collection.create_index('book_id')
        await self.book_collection.create_index('user_id')
        await self.book_collection.create_index([('user_id', 1), ('book_id', 1)])
        await self.book_collection.create_index([('book_id', 1), ('genre', 1)])
        await self.sessions.create_index('user_id')
        await self.sessions.create_index([('user_id', 1), ('created_at', -1)])

    async def create_session(self, session_data: dict):
        """Create new session"""
        from app.DB.mongoDB.monogoDB_schema import SessionModel
        session = SessionModel(**session_data)
        result = await self.sessions.insert_one(session.model_dump(by_alias=True))
        return session

    async def get_session(self, session_id: str):
        """Get session by ID"""
        from app.DB.mongoDB.monogoDB_schema import SessionModel
        session_doc = await self.sessions.find_one({"_id": session_id})
        if session_doc:
            return SessionModel(**session_doc)
        return None
    
    async def update_session(self, session_id: str, update_data: dict):
        """Update session data"""
        result = await self.sessions.update_one(
            {"_id": session_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def insert_story_overview(self, storyline_data: dict):
        """Insert story overview into database"""
        try:
            from app.DB.mongoDB.monogoDB_schema import StorylineModel
            storyline = StorylineModel(**storyline_data)
            result = await self.book_overview_collection.insert_one(
                storyline.model_dump(by_alias=True)
            )
            return str(result.inserted_id)
        except Exception as e:
            raise e
    
    async def get_story_overviews_by_session(self, session_id: str,story_line_id:str):
        """Get all story overviews for a session"""
        cursor =await self.book_overview_collection.find_one({"session_id": session_id,"_id":story_line_id})
        return await cursor.to_list(length=None)
    
    async def get_book_preview(self, session_id: str, preview_count: int = 3):
        try:
            pipeline = [
                # Match the book by session_id
                {'$match': {'session_id': session_id}},
                
                # Lookup and join with pages collection
                {
                    '$lookup': {
                        'from': 'book_pages',  # Your pages collection name
                        'localField': 'page_ids',
                        'foreignField': '_id',
                        'as': 'pages'
                    }
                },
                
                # Project only needed fields and limit pages
                {
                    '$project': {
                        'session_id': 1,
                        'book_id': '$_id',
                        'book_title': 1,
                        'status': 1,
                        'total_pages': {'$size': '$page_ids'},
                        'pages': {
                            '$slice': [
                                {
                                    '$sortArray': {
                                        'input': '$pages',
                                        'sortBy': {'page_number': 1}
                                    }
                                },
                                preview_count
                            ]
                        }
                    }
                }
            ]
            
            cursor = self.book_collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            if not result:
                return None
                
            book_preview = result[0]
            book_preview['preview_count'] = len(book_preview.get('pages', []))
            
            return book_preview
            
        except Exception as e:
            raise e
        
    async def get_full_book(self, session_id: str):
        """Get complete book with all pages using aggregation"""
        try:
            pipeline = [
                # Match the book by session_id
                {'$match': {'session_id': session_id}},
                
                # Lookup and join with pages collection
                {
                    '$lookup': {
                        'from': 'book_pages',  # Your pages collection name
                        'localField': 'page_ids',
                        'foreignField': '_id',
                        'as': 'pages'
                    }
                },
                
                # Sort pages by page_number
                {
                    '$addFields': {
                        'pages': {
                            '$sortArray': {
                                'input': '$pages',
                                'sortBy': {'page_number': 1}
                            }
                        }
                    }
                },
                
                # Project final structure
                {
                    '$project': {
                        'session_id': 1,
                        'book_id': '$_id',
                        'book_title': 1,
                        'status': 1,
                        'pages': 1,
                        'total_pages': {'$size': '$pages'},
                        'created_at': 1,
                        'updated_at': 1,
                        'storyline_id': 1
                    }
                }
            ]
            
            cursor = self.book_collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            return result[0] if result else None
            
        except Exception as e:
            raise e