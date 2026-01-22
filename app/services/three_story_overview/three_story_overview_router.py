from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from ...DB.mongoDB.mongoDB import MongoManager
from .three_story_overview import StoryGenerator
from ...modules.auth.auth import get_current_user
from typing import List, Optional
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


@router.post('/story_overview')
async def generate_three_story_overview(
    background_tasks: BackgroundTasks,
    story_idea: str = Form(...),
    age_range: str = Form(...),
    story_flavours: str = Form(...),
    main_characters: str = Form(...),
    supporting_characters: Optional[str] = Form(None),
    character_personality: Optional[str] = Form(None),
    character_images: Optional[List[UploadFile]] = File(default=[]),
    user = Depends(get_current_user),
    mongo_manager = Depends(get_mongo_manager),
    #s3_manager = Depends(get_s3_manager),
    story_generator = Depends(get_story_generator)
):
    """Generate three story overviews with background image upload"""
    try:
        user_id = user.get("user_id")
        session_id = str(uuid.uuid4())
        book_id = str(uuid.uuid4())
        
        story_flavours_list = json.loads(story_flavours)
        main_characters_list = json.loads(main_characters)
        supporting_characters_list = json.loads(supporting_characters) if supporting_characters else []
        character_personality_dict = json.loads(character_personality) if character_personality else {}
        
        # Create session in MongoDB (without image URLs)
        session_data = {
            "id": session_id,
            "user_id": user_id,
            "story_idea": story_idea,
            "age_range": age_range,
            "story_flavours": story_flavours_list,
            "main_characters": main_characters_list,
            "main_characters_image_url": [],
            "supporting_characters": supporting_characters_list,
            "character_personality": character_personality_dict,
            "illustration_style": [],
            "dedication": [],
            "is_active": True
        }
        
        session = await mongo_manager.create_session(session_data)
        
        # Prepare files for background upload
        if character_images:
            files_to_upload = []
            for image in character_images:
                content = await image.read()
                files_to_upload.append((content, image.filename, image.content_type))
            
            # Schedule background upload
            background_tasks.add_task(
                upload_images_background,
                files_to_upload,
                session_id,
                mongo_manager,
                #s3_manager
            )
        
        # Generate three story overviews (runs immediately)
        story_description = {
            "story_idea": story_idea,
            "age_range": age_range,
            "story_flavours": story_flavours_list,
            "main_characters": main_characters_list,
            "supporting_characters": supporting_characters_list,
            "character_personality": character_personality_dict
        }
        
        ai_response = story_generator.generate_three_story_overview(story_description)
        
        # Store story overviews in MongoDB
        stored_stories = []
        for story in ai_response.get("stories", []):
            storyline_data = {
                "book_id": book_id,
                "user_id": user_id,
                "session_id": session_id,
                "title": story.get("title"),
                "overview": story.get("overview"),
                "genre": story.get("genre"),
                "theme_focus": story.get("theme_focus"),
                "flavour_integration": story.get("flavour_integration")
            }
            
            story_id = await mongo_manager.insert_story_overview(storyline_data)
            storyline_data["id"] = story_id
            stored_stories.append(storyline_data)
        
        return {
            "success": True,
            "session_id": session_id,
            "book_id": book_id,
            "stories": stored_stories,
            "note": "Images are being uploaded in background"
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/session/{session_id}/images')
async def get_session_images(
    session_id: str,
    user = Depends(get_current_user),
    mongo_manager = Depends(get_mongo_manager)
):
    """Get uploaded image URLs for a session"""
    try:
        session = await mongo_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "image_urls": session.main_characters_image_url or [],
            "upload_complete": len(session.main_characters_image_url or []) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




