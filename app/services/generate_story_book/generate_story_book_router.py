from fastapi import APIRouter,HTTPException,Depends
from .three_story_overview import story_overview
from app.modules.auth.auth import get_current_user 
from ...DB.mongoDB.mongoDB import monngoManager
import uuid
router = APIRouter()
story_instance = story_overview()
_monngoManager = monngoManager()
@router.post('/story_overview')
async def generate_three_story_overview(Story_description:dict,user=Depends(get_current_user)):
    try:
        response = story_instance.generate_three_story_overview(Story_description)
        book_id = str(uuid.uuid4())
        user_id = user.get("user_id")
        for story_overviw in response.get("stories",[]):
            story_overview.book_id= book_id
            story_overview.user_id=user_id
            await monngoManager.insert_story_overview(story_overview)
        return response
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
