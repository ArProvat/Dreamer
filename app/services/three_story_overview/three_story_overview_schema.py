from pydantic import BaseModel
from typing import Optional,List
class CharacterModel(BaseModel):
    name: str
    role: str
    species: Optional[str] = None
    age: Optional[str] = None
    traits: Optional[str] = None

class PersonalityQuestionsModel(BaseModel):
    favorite_activity: Optional[str] = None
    biggest_fear: Optional[str] = None
    dream_goal: Optional[str] = None

class CharacterPersonalityModel(BaseModel):
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    motivation: Optional[str] = None

class StoryOverviewRequest(BaseModel):
    story_idea: str
    age_range: str
    story_flavours: List[str]  # Changed to List[str] to match your logic
    main_characters: List[CharacterModel]
    supporting_characters: Optional[List[CharacterModel]] = []
    personality_questions: Optional[PersonalityQuestionsModel] = None
    character_personality: Optional[CharacterPersonalityModel] = None