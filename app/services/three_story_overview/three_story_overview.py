import json
from google import genai
from app.config.config import settings
from app.prompt.prompt import story_overview

class StoryGenerator:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        
    def generate_three_story_overview(self, story_description: dict):
        try:
            formatted_prompt = story_overview.format(**story_description)

            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=formatted_prompt
            )
            
            response_text = response.text.strip()
            
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
                
            return json.loads(response_text.strip())
        except Exception as e:
            print(f"Error: {e}")
            raise e
        
