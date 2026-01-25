from typing import Any, Dict, List, Optional
from pydantic import BaseModel,Field
import uuid
from datetime import datetime


from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class SessionModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    # Session data
    story_idea: Optional[str] = None
    age_range: Optional[str] = None
    story_flavours: Optional[list[str]] = None
    main_characters: Optional[List[Dict[str, Any]]] = None
    main_characters_image_url: Optional[List[str]] = None
    supporting_characters: Optional[List[Dict[str, Any]]] = None
    personality_questions: Optional[Dict[str, Any]] = None
    character_personality: Optional[Dict[str, Any]] = None
    illustration_style: Optional[str] = None
    dedication: Optional[str] = None
    
    class Config:
        populate_by_name = True


class StorylineModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    book_id: str
    user_id: str
    session_id: str
    title: str
    overview: str
    genre: str
    theme_focus: str
    flavour_integration: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
class BookPageModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    book_id: str
    session_id: str
    page_number: int
    page_type: str  # cover, dedication, story, back
    text_content: Optional[str] = None
    image_prompt: Optional[str] = None
    art_direction: Optional[str] = None
    
    image_url: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True