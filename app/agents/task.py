
from crewai import Agent, Task
from typing import Dict, List
import json


def create_planning_task(
    planner: Agent,
    storyline: Dict,
    characters: Dict,
    age_range: str,
    flavours: List[str]
) -> Task:
    """
    Create task for story planning with exact JSON output format
    """
    
    # Define page count based on age range
    page_config = {
        "0-3": {"pages": 10, "words_per_page": "10-20"},
        "4-6": {"pages": 12, "words_per_page": "20-40"},
        "7-9": {"pages": 14, "words_per_page": "25-50"}
    }
    
    config = page_config.get(age_range, {"pages": 12, "words_per_page": "20-40"})
    total_pages = config["pages"]
    
    return Task(
        description=f"""
Create a detailed page-by-page structure for this children's book.

STORYLINE INFORMATION:
Title: {storyline['title']}
Overview: {storyline['overview']}
Emotional Tone: {storyline['emotional_tone']}
Theme: {storyline['theme_focus']}
Genre: {storyline.get('genre', 'adventure')}

CHARACTERS:
{json.dumps(characters, indent=2)}

AGE RANGE: {age_range} years
TOTAL PAGES: {total_pages} (including cover at page 1)
WORDS PER PAGE: {config['words_per_page']}
STORY FLAVOURS: {', '.join(flavours)}

PICTURE BOOK STRUCTURE RULES:
1. Age 0-3: 10 pages total, 10-20 words per page
2. Age 4-6: 12 pages total, 20-40 words per page
3. Age 7-9: 14 pages total, 25-50 words per page
4. Page 1 is always the cover (title only)
5. Simple plot structure with clear beginning, middle, and end
6. No complex sub-plots
7. Age-appropriate content and themes
8. Gentle conflict with positive resolution

YOUR TASK:
Create a page-by-page breakdown that includes:
- Clear story beats for each page
- Emotional journey across pages
- Character focus and development
- Pacing that keeps young readers engaged
- Smooth narrative flow

CRITICAL: You MUST return ONLY valid JSON in this EXACT format:

{{
  "book_structure": {{
    "total_pages": {total_pages},
    "age_range": "{age_range}",
    "narrative_arc": {{
      "beginning": "Pages 1-X: Setup description",
      "middle": "Pages X-Y: Conflict/journey description",
      "end": "Pages Y-{total_pages}: Resolution description"
    }}
  }},
  "pages": [
    {{
      "page_number": 1,
      "page_type": "cover",
      "story_beat": "Title display - {storyline['title']}",
      "emotional_note": "Inviting and exciting",
      "character_focus": "None (cover page)",
      "pacing_guidance": "Eye-catching visual to draw reader in",
      "word_count_target": 0
    }},
    {{
      "page_number": 2,
      "page_type": "story_opening",
      "story_beat": "Introduce main character in their world",
      "emotional_note": "Warm, familiar, comfortable",
      "character_focus": "Main character - establishing personality",
      "pacing_guidance": "Gentle start, set the scene",
      "word_count_target": 25
    }}
    // Continue for all {total_pages} pages
  ]
}}

DO NOT include any markdown formatting, code blocks, or explanatory text.
Return ONLY the raw JSON object.
""",
        expected_output=f"Valid JSON object with book_structure and pages array containing exactly {total_pages} page objects",
        agent=planner
    )


def create_writing_task(
    writer: Agent,
    planning_output: str,
    age_range: str,
    characters: Dict,
    personality_details: Dict,
    dedication: str = None
) -> Task:
    """
    Create task for story writing with exact JSON output format
    """
    
    word_guidance = {
        "0-3": {"min": 10, "max": 20},
        "4-6": {"min": 20, "max": 40},
        "7-9": {"min": 25, "max": 50}
    }
    
    word_limits = word_guidance.get(age_range, {"min": 20, "max": 40})
    
    return Task(
        description=f"""
Write the actual story text for each page based on this structure:

STORY STRUCTURE:
{planning_output}

CHARACTERS:
{json.dumps(characters, indent=2)}

PERSONALITY DETAILS:
{json.dumps(personality_details, indent=2)}

DEDICATION TEXT:
{dedication if dedication else "To be added separately"}

AGE RANGE: {age_range} years
WORD COUNT PER PAGE: {word_limits['min']}-{word_limits['max']} words

WRITING GUIDELINES:
1. Page 1: Title only (book cover) - no story text
2. Pages 2 onwards: Engaging story text
3. Use age-appropriate vocabulary
4. Include sensory details (sights, sounds, feelings)
5. Create magical, memorable moments
6. Incorporate character personalities naturally
7. Maintain consistent voice throughout
8. Use rhythm and repetition where appropriate
9. Build emotional connection
10. End with warmth and satisfaction

CRITICAL: You MUST return ONLY valid JSON in this EXACT format:

{{
  "book_metadata": {{
    "age_range": "{age_range}",
    "total_pages": 12,
    "word_count_range": "{word_limits['min']}-{word_limits['max']} per page"
  }},
  "pages": [
    {{
      "page_number": 1,
      "page_type": "cover",
      "text": "",
      "word_count": 0
    }},
    {{
      "page_number": 2,
      "page_type": "story",
      "text": "Once upon a time...",
      "word_count": 23
    }}
    // Continue for all pages
  ]
}}

DO NOT include any markdown formatting, code blocks, or explanatory text.
Return ONLY the raw JSON object.
""",
        expected_output="Valid JSON object with pages array containing text for all pages",
        agent=writer
    )


def create_art_direction_task(
    art_director: Agent,
    story_text: str,
    characters: Dict,
    style: str
) -> Task:
    """
    Create task for art direction with exact JSON output format
    """
    
    return Task(
        description=f"""
Design the visual scenes for each page of this children's book.

STORY TEXT (ALL PAGES):
{story_text}

CHARACTERS (MUST REMAIN CONSISTENT):
{json.dumps(characters, indent=2)}

ILLUSTRATION STYLE: {style}

CHARACTER CONSISTENCY REQUIREMENTS:
- Face shape, features, and expressions
- Hair color, style, and texture
- Skin tone (exact match)
- Eye color and shape
- Body proportions
- Core outfit colors
- Signature accessories

VISUAL STORYTELLING ELEMENTS:
1. Scene composition and framing
2. Character positions and body language
3. Facial expressions and emotions
4. Background and setting details
5. Lighting direction and mood
6. Color palette and harmony
7. Time of day
8. Weather/atmosphere

CRITICAL: You MUST return ONLY valid JSON in this EXACT format:

{{
  "illustration_guide": {{
    "style": "{style}",
    "color_philosophy": "Overall color approach",
    "consistency_notes": "Key elements identical across all pages"
  }},
  "character_reference": {{
    "main_character": {{
      "name": "Character name",
      "face_shape": "round/oval/square",
      "hair": "brown curly shoulder-length",
      "eyes": "bright blue, large",
      "skin_tone": "light peach",
      "outfit": "yellow sundress with white flowers",
      "signature_item": "butterfly net",
      "body_type": "child proportions, average height"
    }}
  }},
  "pages": [
    {{
      "page_number": 1,
      "page_type": "cover",
      "scene_setting": "magical garden entrance",
      "time_of_day": "golden hour afternoon",
      "weather": "sunny and warm",
      "character_position": "center, welcoming pose",
      "character_expression": "joyful smile",
      "background_elements": ["garden gate", "flowers", "butterflies", "trees"],
      "foreground_elements": ["character", "butterfly net"],
      "color_palette": {{
        "primary": ["soft yellow", "gentle green", "sky blue"],
        "accent": ["pink flowers", "coral butterflies"],
        "mood": "warm and inviting"
      }},
      "lighting": {{
        "direction": "soft overhead, slightly from right",
        "quality": "warm golden glow",
        "shadows": "soft and minimal"
      }},
      "composition": "centered, vertical orientation",
      "visual_focus": "character's welcoming expression",
      "emotional_atmosphere": "excitement and welcome"
    }}
    // Continue for all pages
  ]
}}

DO NOT include any markdown formatting, code blocks, or explanatory text.
Return ONLY the raw JSON object.
""",
        expected_output="Valid JSON object with illustration_guide, character_reference, and pages array",
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
    Enhanced prompt generation with intelligent reference selection
    """
    
    return Task(
        description=f"""
Generate precise image prompts with intelligent reference selection.

ART DIRECTION:
{art_direction}

STORY TEXT:
{story_text}

CHARACTERS:
{json.dumps(characters, indent=2)}

STYLE: {style}
BOOK ID: {book_id}

PROMPT FORMATTING STRUCTURE:

Each prompt MUST follow this exact structure:

[SUBJECT] A [character description] [action/pose]
[SETTING] in [location description] with [background elements]
[STYLE] [illustration style] style, [specific style characteristics]
[LIGHTING] [light direction and quality], [mood]
[COLORS] Color palette: [specific colors]
[MOOD] [emotional atmosphere], [overall feeling]
[QUALITY] Professional children's book illustration, high detail, print-ready
[SAFETY] Child-safe, warm, positive imagery

EXAMPLE FORMATTED PROMPT:
"A cheerful 6-year-old girl with brown curly shoulder-length hair, bright blue eyes, light peach skin, wearing a yellow sundress with white flowers, holding a butterfly net, standing in a welcoming pose. In a magical garden with colorful flowers, stone pathway, wooden gate, and butterflies. Soft pastel storybook illustration style with gentle textures, dreamy atmosphere, and delicate details. Warm golden afternoon lighting from upper right, creating soft shadows. Color palette: soft yellows, gentle greens, sky blues, pink flowers, coral accents. Joyful and inviting atmosphere with sense of wonder. Professional children's book illustration, award-winning quality, high detail suitable for print. Child-safe, warm, positive imagery."

REFERENCE IMAGE SELECTION LOGIC:

For each page, intelligently select 2-3 reference images based on:

1. CHARACTER PROMINENCE MATCHING:
   - If character is prominent → select pages where character is also prominent
   - If character is distant → select similar distant shots
   - Match close-ups with close-ups, full-body with full-body

2. SETTING SIMILARITY:
   - Indoor scenes → reference other indoor scenes
   - Outdoor scenes → reference other outdoor scenes
   - Same location → definitely reference that location

3. LIGHTING/TIME OF DAY:
   - Daytime → reference other daytime scenes
   - Golden hour → reference other golden hour scenes
   - Night → reference other night scenes

4. COLOR PALETTE SIMILARITY:
   - Warm colors → reference warm-colored pages
   - Cool colors → reference cool-colored pages
   - Vibrant → reference vibrant pages

5. RECENCY (Last 1-2 pages for continuity)

SELECTION RULES:
- Page 1 (cover): NO references
- Page 2-3: Reference page 1 only
- Page 4-6: Reference pages 1-2 + most similar scene
- Page 7-10: Reference 1-2 recent pages + 1-2 most similar pages (NOT all previous)
- Page 11+: Reference 2 recent pages + 1-2 most similar pages

DO NOT include all previous pages - be selective!

CRITICAL: Return ONLY valid JSON in this EXACT format:

{{
  "generation_metadata": {{
    "book_id": "{book_id}",
    "illustration_style": "{style}",
    "total_pages": 12
  }},
  "character_consistency_base": {{
    "main_character_full_description": "Complete character description used in EVERY prompt",
    "character_shorthand": "Quick reference - brown curly hair, blue eyes, yellow dress, butterfly net"
  }},
  "pages": [
    {{
      "page_number": 1,
      "page_type": "cover",
      "scene_analysis": {{
        "character_prominence": "high",
        "setting_type": "outdoor",
        "time_of_day": "afternoon",
        "color_temperature": "warm",
        "composition_type": "centered portrait"
      }},
      "formatted_image_prompt": "[Full formatted prompt following the structure above - 150-250 words, highly detailed]",
      "negative_prompt": "scary, dark, violent, weapons, distorted face, uncanny valley, low quality, blurry, deformed, ugly, bad anatomy, wrong proportions, extra limbs, mutations, horror, gore, blood, inappropriate content",
      "reference_selection": {{
        "reference_page_numbers": [],
        "selection_reason": "Cover page - no references needed",
        "reference_count": 0
      }},
      "prompt_components": {{
        "subject": "A cheerful 6-year-old girl...",
        "setting": "magical garden entrance...",
        "style": "soft pastel storybook illustration...",
        "lighting": "warm golden afternoon light...",
        "colors": "soft yellows, gentle greens, sky blues...",
        "mood": "joyful and inviting...",
        "quality": "professional, award-winning, print-ready",
        "safety": "child-safe, warm, positive"
      }},
      "technical_parameters": {{
        "aspect_ratio": "portrait",
        "detail_level": "high",
        "color_saturation": "soft/moderate",
        "contrast": "gentle"
      }}
    }},
    {{
      "page_number": 2,
      "page_type": "story",
      "scene_analysis": {{
        "character_prominence": "high",
        "setting_type": "outdoor",
        "time_of_day": "afternoon",
        "color_temperature": "warm",
        "composition_type": "medium shot"
      }},
      "formatted_image_prompt": "[SAME CHARACTER: brown curly shoulder-length hair, bright blue eyes, light peach skin, yellow sundress with white flowers, butterfly net] A cheerful girl crouching down examining flowers with curiosity. In a magical garden path with colorful blooms, stepping stones, garden tools, and fluttering butterflies around her. Soft pastel storybook illustration style with gentle brushstrokes, dreamy quality, delicate textures. Warm afternoon sunlight filtering through leaves, creating dappled light patterns. Color palette: soft yellows, lavender purples, rose pinks, sage greens, warm golden tones. Wonder and discovery atmosphere, gentle and engaging. Professional children's book illustration, consistent with previous page, high quality, print-ready. Child-safe, warm, positive imagery.",
      "negative_prompt": "character inconsistency, different hair, different outfit, different face, scary, dark, dangerous, low quality, blurry, distorted features, wrong colors, style mismatch",
      "reference_selection": {{
        "reference_page_numbers": [1],
        "selection_reason": "Page 1 has same character prominence, outdoor setting, warm lighting - perfect for consistency",
        "reference_count": 1
      }},
      "prompt_components": {{
        "subject": "SAME CHARACTER as page 1 - girl crouching examining flowers...",
        "setting": "magical garden path with flowers and stepping stones...",
        "style": "soft pastel storybook, consistent with page 1...",
        "lighting": "warm afternoon sunlight, dappled through leaves...",
        "colors": "yellows, purples, pinks, greens, golden tones...",
        "mood": "wonder and discovery...",
        "quality": "professional, consistent with previous page",
        "safety": "child-safe, warm, positive"
      }},
      "technical_parameters": {{
        "aspect_ratio": "landscape",
        "detail_level": "high",
        "color_saturation": "soft",
        "contrast": "gentle"
      }}
    }},
    {{
      "page_number": 10,
      "page_type": "story",
      "scene_analysis": {{
        "character_prominence": "medium",
        "setting_type": "outdoor",
        "time_of_day": "golden_hour",
        "color_temperature": "very_warm",
        "composition_type": "wide landscape"
      }},
      "formatted_image_prompt": "[Complete detailed prompt...]",
      "negative_prompt": "...",
      "reference_selection": {{
        "reference_page_numbers": [8, 9, 3],
        "selection_reason": "Page 8-9 for continuity (recent pages), Page 3 for similar outdoor wide landscape composition with golden hour lighting - NOT using pages 1,2,4,5,6,7 as they have different composition/lighting",
        "reference_count": 3
      }},
      "prompt_components": {{}},
      "technical_parameters": {{}}
    }}
    // Continue for ALL pages with intelligent reference selection
  ]
}}

CRITICAL RULES:
1. EVERY prompt must be 150-250 words, highly detailed
2. Character description MUST be IDENTICAL in every prompt
3. Format prompts using the structure provided
4. Select 0-3 references per page based on similarity, NOT chronological order
5. For page 10, DO NOT reference all pages 1-9, select most similar 2-3 pages
6. Include detailed scene_analysis for each page
7. Provide clear selection_reason for each reference choice
8. Make prompts specific enough to generate without ambiguity

DO NOT include markdown, code blocks, or explanatory text.
Return ONLY the raw JSON object.
""",
        expected_output="Valid JSON with detailed prompts and intelligent reference selection for all pages",
        agent=prompt_engineer
    )


