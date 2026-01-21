
from pydantic import BaseModel,Field
import uuid
from datetime import datetime


class StorylineModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    session_id: str
    
    title: str
    overview: str
    emotional_tone: str
    theme_focus: str
    genre: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_selected: bool = False
    
    class Config:
        populate_by_name = True

