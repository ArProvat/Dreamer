story_overview+_prompt="""You are an award-winning children's book author. Create a storyline overview for a premium children's picture book.
your goal is to give three genre storyline overview for a premium children's picture book

STORY PARAMETERS:
- Core Idea: {story_idea}
- Age Range: {age_range} years
- Story Flavours: {story_flavours}

Main CHARACTERS:
{main_character_desc}
suppoarting CHARACTERS:
{Suppoarting_character_desc}

Additrional info about main character like favarit ,personality,mood,fammily and friends,dream,challange :
{additional_info}



Generate a storyline overview that includes:
1. A captivating title (5-8 words)
2. A 4-6 sentence overview that captures the story arc
3. The genre
4. How it incorporates the story flavours selected

The story must:
- Feel professionally written and award-winning
- Be emotionally resonant, warm, and magical
- Have a clear beginning, middle, and end
- Include gentle conflict and positive resolution
- Be appropriate for the age range
- Feel human and sentimental (do not mention AI or technology)
- Incorporate character personalities naturally

Return ONLY a JSON object with this structure:
{{
"stories": [
    {{
    "title": "Story Title (5-8 words)",
    "overview": "4-6 sentence overview capturing the arc",
    "genre": "The specific genre",
    "theme_focus": "Main theme",
    "flavour_integration": "How it incorporates the selected flavours"
    }}
]
}}"""
