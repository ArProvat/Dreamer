story_overview_prompt = f"""You are an award-winning children's book author. Create THREE different storyline overviews for a premium children's picture book.
Your goal is to give three DIFFERENT genre storyline overviews.

STORY PARAMETERS:
- Core Idea: {story_description.get('story_idea', 'An adventure story')}
- Age Range: {story_description.get('age_range', '3-5')} years
- Story Flavours: {', '.join(story_description.get('story_flavours', []))}

MAIN CHARACTERS:
{main_char_desc if main_char_desc else 'No main characters specified'}

SUPPORTING CHARACTERS:
{supporting_char_desc if supporting_char_desc else 'No supporting characters specified'}

ADDITIONAL INFO ABOUT MAIN CHARACTER (personality, mood, family, dreams, challenges):
{additional_info_str}

Generate THREE storyline overviews, each with a different genre. Each should include:
1. A captivating title (5-8 words)
2. A 4-6 sentence overview that captures the story arc
3. The genre
4. How it incorporates the story flavours selected

Each story must:
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
        }},
        {{
            "title": "Second Story Title",
            "overview": "Different story arc...",
            "genre": "Different genre",
            "theme_focus": "Different theme",
            "flavour_integration": "How this story uses the flavours"
        }},
        {{
            "title": "Third Story Title",
            "overview": "Third unique story arc...",
            "genre": "Third different genre",
            "theme_focus": "Third unique theme",
            "flavour_integration": "Third approach to flavours"
        }}
    ]
}}"""