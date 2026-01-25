import asyncio
import json
from google import genai
from app.config.config import settings
from app.prompt.prompt import story_overview_prompt

class StoryGenerator:
    def __init__(self):
        # Ensure your settings are correctly imported
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        
    async def generate_three_story_overview(self, story_description: dict):
        max_retries = 3
        retry_delay = 5  # Start with 5 seconds

        for attempt in range(max_retries):
            try:
                formatted_prompt = await self._format_prompt(story_description)
                print(formatted_prompt)
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash-lite',
                    contents=formatted_prompt
                )
                
                response_text = response.text.strip()
                
                # Cleaning Markdown
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]
                    
                return json.loads(response_text.strip())

            except Exception as e:
                # Check if it's a rate limit error (429)
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"Rate limit hit. Retrying in {retry_delay} seconds... (Attempt {attempt + 1})")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                
                print(f"AI Generation Error: {e}")
                raise e
        
    async def _format_prompt(self, story_description: dict) -> str:
        # Format main characters
        main_chars = story_description.get('main_characters', [])
        main_char_desc = "\n".join([
            f"- {char.get('name', 'Unknown')}: {char.get('traits', char.get('description', 'No description'))}"
            for char in main_chars
        ])
        
        supporting_chars = story_description.get('supporting_characters', [])
        supporting_char_desc = "\n".join([
            f"- {char.get('name', 'Unknown')}: {char.get('traits', char.get('description', 'No description'))}"
            for char in supporting_chars
        ])
        
        additional_info_json = json.dumps(story_description.get('character_personality', {}), indent=2)

        return story_overview_prompt.format(
            core_idea=story_description.get('story_idea', 'An adventure'),
            age_range=story_description.get('age_range', '3-5'),
            story_flavours=', '.join(story_description.get('story_flavours', [])),
            main_char_desc=main_char_desc,
            supporting_char_desc=supporting_char_desc,
            additional_info_str=additional_info_json 
        )