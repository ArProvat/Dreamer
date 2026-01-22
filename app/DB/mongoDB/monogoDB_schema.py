
from pydantic import BaseModel,Field
import uuid
from datetime import datetime


class StorylineModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id:str
    book_id: str
    title: str
    overview: str
    genre: str
    theme_focus: str
    flavour_integration:str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_selected: bool = False
    
    class Config:
        populate_by_name = True

