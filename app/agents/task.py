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
    }},
    {{
      "page_number": 3,
      "page_type": "story",
      "story_beat": "Show character's normal life/routine",
      "emotional_note": "Cheerful, relatable",
      "character_focus": "Main character with supporting characters",
      "pacing_guidance": "Build connection with character",
      "word_count_target": 30
    }}
    // Continue for all {total_pages} pages following this structure
  ]
}}

IMPORTANT INSTRUCTIONS:
1. Return ONLY the JSON object above, no additional text
2. Include ALL {total_pages} pages in the "pages" array
3. Page 1 must be cover type
4. Ensure story has clear beginning (setup), middle (challenge), and end (resolution)
5. Emotional journey should build and resolve satisfyingly
6. Each page must advance the story meaningfully
7. Match word count targets to age range guidelines

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
8. Use rhythm and repetition where appropriate (especially for younger ages)
9. Build emotional connection
10. End with warmth and satisfaction

STYLE REQUIREMENTS:
- Professional, award-winning quality
- Emotionally resonant and warm
- Beautiful, accessible language
- Perfect flow from page to page
- Show, don't tell (where age-appropriate)
- Use dialogue to bring characters to life
- Create vivid, imaginative scenes

CRITICAL: You MUST return ONLY valid JSON in this EXACT format:

{{
  "book_metadata": {{
    "age_range": "{age_range}",
    "total_pages": 12,
    "word_count_range": "{word_limits['min']}-{word_limits['max']} per page",
    "writing_style": "Award-winning children's literature"
  }},
  "pages": [
    {{
      "page_number": 1,
      "page_type": "cover",
      "text": "",
      "word_count": 0,
      "notes": "Cover page - visual only"
    }},
    {{
      "page_number": 2,
      "page_type": "story",
      "text": "Once upon a time, in a cozy little house at the edge of a magical garden, lived a curious girl named Emma.",
      "word_count": 23,
      "notes": "Opening - introduces main character"
    }},
    {{
      "page_number": 3,
      "page_type": "story",
      "text": "Every morning, Emma would wake up to the sound of birds singing and butterflies dancing outside her window. Today felt different—today felt special.",
      "word_count": 25,
      "notes": "Setup - establishes setting and hints at adventure"
    }}
    // Continue for all pages
  ]
}}

IMPORTANT INSTRUCTIONS:
1. Return ONLY the JSON object above, no additional text
2. Include text for ALL pages (except page 1 which is cover)
3. Each page's text must be within the word count range
4. Ensure story flows naturally from page to page
5. Use proper punctuation and grammar
6. Text should match the story beats from the planning phase
7. Create emotional resonance appropriate for age group

DO NOT include any markdown formatting, code blocks, or explanatory text.
Return ONLY the raw JSON object.
""",
        expected_output="Valid JSON object with book_metadata and pages array containing text for all pages with exact word counts",
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
1. Face shape, features, and expressions
2. Hair color, style, and texture
3. Skin tone (exact match across all pages)
4. Eye color and shape
5. Body proportions and build
6. Core outfit design and colors
7. Signature accessories or items
8. Overall character silhouette

ILLUSTRATION STYLE GUIDELINES:

{style} - Characteristics:
""" + ("""
- Soft, dreamy pastels (pinks, lavenders, soft blues, gentle yellows)
- Delicate textures and gentle shading
- Slightly muted, calming color palette
- Classic storybook illustration feel
- Warm, nostalgic atmosphere
""" if style == "Soft Pastel Storybook" else """
- Flowing, translucent watercolor effects
- Color bleeding and soft edges
- Layered washes of color
- Natural, organic feel
- Emotional depth through color blending
- White space and negative space usage
""" if style == "Watercolour Wash" else """
- Bold, solid colors with clear boundaries
- Flat shapes without gradients
- Modern, playful aesthetic
- Vibrant, saturated color palette
- Clean lines and geometric simplicity
- Crisp, contemporary look
""" if style == "Clean Digital Flat Art" else """
- Dimensional characters and objects
- Soft lighting and shadows
- Tactile, touchable quality
- Depth and perspective
- Rounded, friendly forms
- Warm, inviting scenes
""") + f"""

SAFETY REQUIREMENTS (MANDATORY):
✓ Soft, warm, positive imagery only
✓ Friendly, approachable characters
✓ Safe, nurturing environments
✗ NO violence, weapons, or fighting
✗ NO scary faces, monsters, or dark themes
✗ NO distorted or uncanny features
✗ NO dangerous situations (heights, fire, water hazards)
✗ NO sad or distressing scenes

VISUAL STORYTELLING ELEMENTS:
1. Scene composition and framing
2. Character positions and body language
3. Facial expressions and emotions
4. Background and setting details
5. Lighting direction and mood
6. Color palette and harmony
7. Focus points and visual hierarchy
8. Atmospheric elements

CRITICAL: You MUST return ONLY valid JSON in this EXACT format:

{{{{
  "illustration_guide": {{{{
    "style": "{style}",
    "color_philosophy": "Describe overall color approach",
    "consistency_notes": "Key elements that must remain identical across all pages"
  }}}},
  "character_reference": {{{{
    "main_character": {{{{
      "name": "Character name",
      "visual_identity": {{{{
        "face_shape": "Description",
        "hair": "Color, style, length",
        "eyes": "Color and shape",
        "skin_tone": "Exact description",
        "outfit": "Main clothing items and colors",
        "signature_item": "Key accessory or prop",
        "body_type": "Build and proportions"
      }}}}
    }}}},
    "supporting_characters": [
      {{{{
        "name": "Character name",
        "visual_identity": {{{{
          "description": "Complete visual description"
        }}}}
      }}}}
    ]
  }}}},
  "pages": [
    {{{{
      "page_number": 1,
      "page_type": "cover",
      "scene_composition": {{{{
        "framing": "Full cover illustration",
        "focal_point": "Title and main character",
        "layout": "Centered composition"
      }}}},
      "visual_description": "Main character in heroic or welcoming pose, surrounded by key story elements. Title prominently displayed.",
      "characters_present": ["Main character name"],
      "character_details": {{{{
        "main_character": {{{{
          "position": "Center of composition",
          "expression": "Warm, inviting smile",
          "body_language": "Open, welcoming pose",
          "outfit_details": "Full outfit visible"
        }}}}
      }}}},
      "setting": {{{{
        "location": "Key story location",
        "time_of_day": "Bright daylight",
        "weather": "Clear and pleasant",
        "background_elements": ["tree", "flowers", "path"]
      }}}},
      "lighting": {{{{
        "direction": "Soft overhead light",
        "mood": "Warm and inviting",
        "shadows": "Gentle, non-threatening"
      }}}},
      "color_palette": {{{{
        "primary_colors": ["soft yellow", "gentle green", "sky blue"],
        "accent_colors": ["pink", "coral"],
        "overall_tone": "Bright and cheerful"
      }}}},
      "emotional_atmosphere": "Excitement and welcome",
      "key_visual_elements": ["title text", "main character", "story setting preview"],
      "style_notes": "Set the visual tone for entire book"
    }}}},
    {{{{
      "page_number": 2,
      "page_type": "story",
      "scene_composition": {{{{
        "framing": "Medium shot of character in environment",
        "focal_point": "Character's face and expression",
        "layout": "Character on left, setting on right"
      }}}},
      "visual_description": "Character in their familiar environment, showing personality and daily life.",
      "characters_present": ["Main character"],
      "character_details": {{{{
        "main_character": {{{{
          "position": "Left third of frame",
          "expression": "Curious and content",
          "body_language": "Relaxed, natural pose",
          "outfit_details": "Same as cover - maintain consistency"
        }}}}
      }}}},
      "setting": {{{{
        "location": "Character's home/familiar place",
        "time_of_day": "Morning",
        "weather": "Sunny",
        "background_elements": ["furniture", "windows", "personal items"]
      }}}},
      "lighting": {{{{
        "direction": "Window light from right",
        "mood": "Warm morning glow",
        "shadows": "Soft and minimal"
      }}}},
      "color_palette": {{{{
        "primary_colors": ["warm yellow", "soft brown", "cream"],
        "accent_colors": ["character outfit colors"],
        "overall_tone": "Cozy and familiar"
      }}}},
      "emotional_atmosphere": "Comfort and belonging",
      "key_visual_elements": ["character", "home setting", "morning light"],
      "style_notes": "Establish character's world"
    }}}}
    // Continue for ALL pages
  ]
}}}}

IMPORTANT INSTRUCTIONS:
1. Return ONLY the JSON object above, no additional text
2. Include visual direction for ALL pages
3. Maintain exact character consistency across all pages
4. Ensure safety requirements are met in every scene
5. Match visual tone to story text
6. Create clear, detailed descriptions for image generation
7. Specify all key visual elements needed

DO NOT include any markdown formatting, code blocks, or explanatory text.
Return ONLY the raw JSON object.
""",
        expected_output="Valid JSON object with illustration_guide, character_reference, and pages array containing detailed art direction for all pages",
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
    Create task for generating precise image prompts
    """
    
    return Task(
        description=f"""
Generate precise, detailed image generation prompts for each page.

ART DIRECTION (COMPLETE VISUAL GUIDE):
{art_direction}

STORY TEXT (ALL PAGES):
{story_text}

CHARACTERS (CONSISTENCY CRITICAL):
{json.dumps(characters, indent=2)}

ILLUSTRATION STYLE: {style}
BOOK ID: {book_id}

IMAGE GENERATION PROMPT REQUIREMENTS:

1. CHARACTER CONSISTENCY ELEMENTS:
   - Start every prompt with detailed character description
   - Include: face shape, hair (color/style), skin tone, eyes, outfit, signature items
   - Reference "maintaining exact appearance from previous illustrations"
   - Specify any character differences from reference images must be rejected

2. STYLE SPECIFICATIONS:
   - Clearly state the illustration style: {style}
   - Include style-specific techniques and characteristics
   - Specify color palette and mood
   - Detail texture and rendering approach

3. SCENE DESCRIPTION:
   - Composition and framing
   - Character positions and actions
   - Background and setting elements
   - Lighting direction and quality
   - Emotional atmosphere

4. SAFETY CONSTRAINTS:
   - Explicitly state "child-safe, warm, positive imagery"
   - Exclude any potentially scary or unsafe elements
   - Ensure friendly, approachable visual tone

5. TECHNICAL SPECIFICATIONS:
   - High quality, professional illustration
   - Suitable for print reproduction
   - Age-appropriate visual complexity

CRITICAL: You MUST return ONLY valid JSON in this EXACT format:

{{
  "generation_metadata": {{
    "book_id": "{book_id}",
    "illustration_style": "{style}",
    "total_pages": 12,
    "character_consistency_priority": "highest",
    "safety_validation": "enabled"
  }},
  "character_consistency_base": {{
    "main_character_description": "Complete detailed description used in ALL prompts for consistency",
    "visual_signature": "Key identifying features that must appear in every image"
  }},
  "pages": [
    {{
      "page_number": 1,
      "page_type": "cover",
      "story_context": "Cover page introducing the story",
      "image_prompt": "A premium children's book cover illustration in {style} style. [MAIN CHARACTER: detailed physical description including face shape, hair color and style, skin tone, eye color, outfit description, signature item]. Character in welcoming pose at center. Background shows [setting elements]. Soft, warm lighting. Color palette: [specific colors]. Professional, award-winning quality. Child-safe, positive imagery. High detail, suitable for print.",
      "consistency_requirements": [
        "Exact character appearance as described",
        "Style must match {style} precisely",
        "Safety validation required"
      ],
      "negative_prompt": "scary, dark, violent, weapons, distorted face, uncanny valley, low quality, blurry, inappropriate",
      "expected_elements": [
        "Main character in correct appearance",
        "Title space",
        "Story setting preview",
        "Warm, inviting atmosphere"
      ],
      "safety_check": {{
        "approved_content": ["friendly character", "bright colors", "welcoming scene"],
        "forbidden_content": ["weapons", "scary elements", "danger"]
      }}
    }},
    {{
      "page_number": 2,
      "page_type": "story",
      "story_context": "Text from page 2 of story",
      "image_prompt": "[MAIN CHARACTER: SAME exact description as page 1 - face shape, hair, skin tone, eyes, outfit, signature item - NO VARIATIONS]. Character positioned [position] with [expression] expression and [body language]. Setting: [detailed setting description]. Background elements: [specific items]. Lighting: [direction and quality]. {style} illustration style with [specific style elements]. Color palette: [colors matching overall book]. Warm, positive, child-safe scene. Professional quality, print-ready.",
      "consistency_requirements": [
        "Character MUST match page 1 exactly",
        "Maintain same outfit and accessories",
        "Identical facial features",
        "Reference previous page images for validation"
      ],
      "negative_prompt": "character inconsistency, different appearance, style mismatch, scary, dark, dangerous, low quality, distorted features",
      "expected_elements": [
        "Character in exact same appearance",
        "Setting matching story text",
        "Appropriate emotional tone",
        "Style consistency"
      ],
      "safety_check": {{
        "approved_content": ["safe environment", "positive interaction", "age-appropriate scene"],
        "forbidden_content": ["hazards", "scary faces", "violence"]
      }},
      "reference_images": {{
        "previous_pages": [1],
        "consistency_check": "Validate character appearance matches page 1"
      }}
    }}
    // Continue for ALL pages with same detailed structure
  ],
  "generation_instructions": {{
    "sequence": "Generate pages in order 1 through 12",
    "validation_process": "Each image must pass safety check and consistency validation before approval",
    "retry_logic": "If consistency score < 85% or safety check fails, regenerate with strengthened prompt",
    "reference_usage": "Always include previous page images as reference for character consistency"
  }}
}}

CRITICAL PROMPT ENGINEERING RULES:
1. Every prompt must include COMPLETE character description
2. Character description must be IDENTICAL across all pages
3. Reference previous pages explicitly for consistency
4. Include both positive (what to include) and negative (what to exclude) specifications
5. Be extremely detailed about style characteristics
6. Specify exact color palettes
7. Include safety requirements in every prompt
8. Make prompts detailed enough for AI to generate without ambiguity

IMPORTANT INSTRUCTIONS:
1. Return ONLY the JSON object above, no additional text
2. Include complete prompts for ALL pages
3. Ensure character consistency across all prompts
4. Include safety specifications in every prompt
5. Make prompts detailed and comprehensive
6. Specify negative prompts to avoid unwanted elements

DO NOT include any markdown formatting, code blocks, or explanatory text.
Return ONLY the raw JSON object.
""",
        expected_output="Valid JSON object with generation_metadata, character_consistency_base, pages array containing detailed image generation prompts for all pages, and generation_instructions",
        agent=prompt_engineer
    )

