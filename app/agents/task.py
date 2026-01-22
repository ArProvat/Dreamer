from crewai import Agent ,Task
from typing import Dict,List
import json


def create_planning_task(
    planner: Agent,
    storyline: Dict,
    characters: Dict,
    age_range: str,
    flavours: List[str]
) -> Task:
    """
    Create task for story planning
    """
    return Task(
        description=f"""
Create a detailed  structure for this children's book:

STORYLINE: {storyline['title']}
Overview: {storyline['overview']}
Emotional Tone: {storyline['emotional_tone']}
Theme: {storyline['theme_focus']}

CHARACTERS: {json.dumps(characters, indent=2)}
AGE RANGE: {age_range}
STORY FLAVOURS: {', '.join(flavours)}
rules:
Enforce picture-book rules based on the age range:
1. Age 0–3: 8–10 pages, 10–20 words per page.
2. Age 4–6: 10–12 pages, 20–40 words per page.
3. Age 7–9: 12–14 pages, 25–50 words per page.
4. Simple plot structure, no sub-plots.
5. Ensure age-appropriate content.

Create a page-by-page breakdown with:
1. Page number (1-24, where page 1 is cover, page 2 is dedication)
2. Story beat/moment for each page
3. Emotional note for each page
4. Character focus for each page
5. Pacing guidance

Ensure smooth narrative flow with clear beginning, middle, and end.
Include gentle conflict and positive resolution.
Make it feel award-winning and emotionally resonant.
""",
        expected_output="JSON structure with page breakdown including beats, emotions, and pacing",
        agent=planner
    )

def create_writing_task(
    writer: Agent,
    planning_output: str,
    age_range: str,
    characters: Dict,
    personality_details: Dict
) -> Task:
    """
    Create task for story writing
    """
    word_guidance = {
        "0-3": "10-20 words",
        "4-6": "20-35 words",
        "7-9": "25-45 words"
    }
    
    return Task(
        description=f"""
Based on this story structure:
{planning_output}

Write the actual text for each of the 24 pages.

CHARACTERS: {json.dumps(characters, indent=2)}
PERSONALITY DETAILS: {json.dumps(personality_details, indent=2)}
WORDS PER PAGE: {word_guidance.get(age_range, '20-35 words')}

Requirements:
- Page 1: Title only (book cover)
- Page 2: Dedication text (already provided separately)
- Pages 3-rest of the page: Story text following the structure

The writing must:
- Feel professionally written and award-winning
- Be emotionally resonant and warm
- Flow beautifully from page to page
- Use age-appropriate vocabulary
- Include sensory details and magical moments
- Incorporate character personalities naturally
- Have beautiful, accessible language

Return JSON with page number and text for each page.
""",
        expected_output="JSON structure with text for all 24 pages",
        agent=writer
    )

def create_art_direction_task(
    art_director: Agent,
    story_text: str,
    characters: Dict,
    style: str
) -> Task:
    """
    Create task for art direction
    """
    return Task(
        description=f"""
Based on this story text:
{story_text}

Design the visual scenes for each page.

CHARACTERS (must remain consistent): {json.dumps(characters, indent=2)}
ILLUSTRATION STYLE: {style}

For each page, describe:
1. Scene composition and framing
2. Character positions and expressions
3. Background and setting details
4. Lighting and mood
5. Color palette
6. Key visual elements
7. Emotional atmosphere

CRITICAL CONSISTENCY REQUIREMENTS:
- Characters must look identical across all pages
- Same face shape, hair color/style, skin tone
- Same core outfit colors
- Same body proportions
- Same signature accessories

SAFETY REQUIREMENTS:
- Only soft, warm, positive imagery
- No violence, weapons, or scary elements
- No distorted faces
- No dangerous scenarios

Return JSON with detailed visual direction for each page.
""",
        expected_output="JSON structure with art direction for all 24 pages",
        agent=art_director
    )

def create_prompt_generation_task(
    prompt_engineer: Agent,
    art_direction: str,
    story_text: str,
    characters: Dict,
    style: str,
    book_id: str
) -> Task:
    """
    Create task for generating image prompts and images
    """
    return Task(
        description=f"""
Generate precise image generation prompts and create images for each page.

ART DIRECTION: {art_direction}
STORY TEXT: {story_text}
CHARACTERS: {json.dumps(characters, indent=2)}
STYLE: {style}
BOOK ID: {book_id}

For each page:
1. Create a detailed image generation prompt
2. Include character consistency details
3. Specify style requirements
4. Include safety constraints
6. Verify character consistency with previous images

Pass previous generated images to maintain consistency.

Return JSON with prompts and image generation results for all pages.
""",
        expected_output="JSON structure with image prompts and generation results",
        agent=prompt_engineer
    )
