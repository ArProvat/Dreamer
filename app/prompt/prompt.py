story_overview=f"""You are an award-winning children's book author. Create a storyline overview for a premium children's picture book.
your goal is to give three genre storyline overview for a premium children's picture book

STORY PARAMETERS:
- Core Idea: {Story_description["story_idea"]}
- Age Range: {Story_description[age_range]} years
- Story Flavours: {Story_description[story_flavours]}

Main CHARACTERS:
{Story_description['main_character_desc']}
suppoarting CHARACTERS:
{Story_description['Suppoarting_character_desc']}

Additrional info about main character like favarit ,personality,mood,fammily and friends,dream,challange :
{Story_description["additional info"]}



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
{"story":[{
    "title": "Story Title",
    "overview": "4-6 sentence overview",
    "genre": "genre",
    "theme_focus": "Main theme",
    "narrative_arc": "Brief description of story structure"
}]}"""
