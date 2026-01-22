import json
from google import genai
from app.config.config import settings
from app.prompt.prompt import story_overview_prompt

class StoryGenerator:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        
    def generate_three_story_overview(self, story_description: dict):
        try:
            formatted_prompt = self._format_prompt()

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
        
    def _format_prompt(self, story_description: dict) -> str:
            """Format the story generation prompt"""
            
            # Format main characters
            main_chars = story_description.get('main_characters', [])
            main_char_desc = "\n".join([
                f"- {char.get('name', 'Unknown')}: {char.get('description', 'No description')}"
                for char in main_chars
            ])
            
            supporting_chars = story_description.get('supporting_characters', [])
            supporting_char_desc = "\n".join([
                f"- {char.get('name', 'Unknown')}: {char.get('description', 'No description')}"
                for char in supporting_chars
            ])
            
            additional_info = story_description.get('character_personality', {})
            additional_info_str = json.dumps(additional_info, indent=2)

            return story_overview_prompt.format(story_description,main_char_desc,supporting_char_desc,additional_info_str)

            