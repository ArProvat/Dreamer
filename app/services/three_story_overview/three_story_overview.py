import json
from google import genai
from app.config.config import settings
from app.prompt.prompt import story_overview

class story_overview:
    def __init__(self):
        self.client = genai.Client(settings.GOOGLE_API_KEY)
        
    async def generate_three_story_overview(self,Story_description:dict):
        """ Generate three genre story overview of the given idea """
        try:
            prompt= story_overview.format(Story_description)

            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                prompt=prompt
                )
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
                
            story_data = json.loads(response_text.strip())
                
            return story_data
        except Exception as e:
            raise e
        
