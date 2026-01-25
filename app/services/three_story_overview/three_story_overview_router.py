from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks,Body
from ...DB.mongoDB.mongoDB import MongoManager
from .three_story_overview import StoryGenerator
from ...modules.auth.auth import get_current_user
from .three_story_overview_schema import StoryOverviewRequest
from typing import Dict, List, Optional
import uuid
import json

router = APIRouter()
async def get_mongo_manager():
    manager = MongoManager()
    await manager.initialize()
    return manager

'''
async def get_s3_manager():
    
    return S3Manager(
        aws_access_key=settings.AWS_ACCESS_KEY,
        aws_secret_key=settings.AWS_SECRET_KEY,
        bucket_name=settings.S3_BUCKET_NAME,
        region=settings.AWS_REGION
    )
'''
async def get_story_generator():
    return StoryGenerator()

async def upload_images_background(
    files_data: List[tuple],
    session_id: str,
    mongo_manager,
    s3_manager
):
    """Background task to upload images and update session"""
    try:
        image_urls = await s3_manager.upload_multiple_images(files_data) #%%
        
        # Update session with image URLs
        await mongo_manager.update_session(
            session_id,
            {"main_characters_image_url": image_urls}
        )
    except Exception as e:
        print(f"Background image upload failed: {str(e)}")
import json
from typing import Any
def parse_form_field(field_value: str):
    """Safely parse a form field that could be JSON or a comma-separated string."""
    if not field_value or field_value.strip() == "":
        return []
    
    field_value = field_value.strip()
    
    # Check if it looks like JSON (starts with [ or {)
    if field_value.startswith(('[', '{')):
        try:
            return json.loads(field_value)
        except json.JSONDecodeError:
            pass 
            
    if "," in field_value:
        return [item.strip() for item in field_value.split(",")]
    
    # Single item fallback
    return [field_value]

@router.post('/story_overview')
async def generate_three_story_overview(
    background_tasks: BackgroundTasks,
    request: StoryOverviewRequest,  # FastAPI automatically parses JSON body here
    user = Depends(get_current_user),
    mongo_manager = Depends(get_mongo_manager),
    story_generator = Depends(get_story_generator)
):
    try:
        user_id = user.get("id") or user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user token")
        
        session_id = str(uuid.uuid4())
        book_id = str(uuid.uuid4())

        # FIX 1: Convert Pydantic models to dictionaries for MongoDB
        # We use .model_dump() (Pydantic v2) or .dict() (Pydantic v1)
        main_chars_data = [char.model_dump() for char in request.main_characters]
        supp_chars_data = [char.model_dump() for char in request.supporting_characters]
        
        # Create session in MongoDB
        session_data = {
            "id": session_id,
            "user_id": str(user_id),
            "story_idea": request.story_idea,
            "age_range": request.age_range,
            "story_flavours": request.story_flavours,
            "main_characters": main_chars_data,
            "main_characters_image_url": [],
            "supporting_characters": supp_chars_data,
            "personality_questions": request.personality_questions.model_dump() if request.personality_questions else {},
            "character_personality": request.character_personality.model_dump() if request.character_personality else {},
            "is_active": True
        }
        await mongo_manager.create_session(session_data)

        # Generate overviews
        # FIX 2: Use the attributes directly from the request object
        story_description = {
            "story_idea": request.story_idea,
            "age_range": request.age_range,
            "story_flavours": request.story_flavours,
            "main_characters": main_chars_data,
            "supporting_characters": supp_chars_data,
            "character_personality": request.character_personality.model_dump() if request.character_personality else {}
        }
        
        ai_response = await story_generator.generate_three_story_overview(story_description)
        
        stored_stories = []
        stories_to_process = ai_response.get("stories", []) if ai_response else []
        
        for story in stories_to_process:
            storyline_data = {
                "book_id": book_id,
                "user_id": str(user_id),
                "session_id": session_id,
                "title": story.get("title"),
                "overview": story.get("overview"),
                "genre": story.get("genre"),
                "theme_focus": story.get("theme_focus"),
                "flavour_integration": story.get("flavour_integration")
            }
            story_id = await mongo_manager.insert_story_overview(storyline_data)
            storyline_data["id"] = str(story_id)
            stored_stories.append(storyline_data)
        
        return {
            "success": True,
            "session_id": session_id,
            "book_id": book_id,
            "stories": stored_stories
        }
        
    except Exception as e:
        print(f"Error: {e}")
        # Log the full error for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))