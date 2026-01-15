from crewai import Task


def create_tasks(config: StoryConfig, agents):
    """Create all tasks for the storybook generation crew"""
    
    story_planner, story_writer, art_director, image_prompt_agent = agents
    
    # Task 1: Plan the Story
    task_plan_story = Task(
        description=f"""
        Create a detailed {config.num_pages}-page story structure based on:
        - Story Idea: {config.story_idea}
        - Age Group: {config.age_group}
        - Main Character: {config.main_character}
        - Supporting Characters: {', '.join(config.supporting_characters)}
        - Story Flavours: {', '.join(config.story_flavours)}
        
        For each page, provide:
        1. Page number
        2. Scene summary (what happens)
        3. Key emotions or themes
        4. Character actions
        5. Story progression notes
        
        Ensure the story has:
        - Clear beginning, middle, and end
        - Age-appropriate challenges and resolution
        - Character development
        - Incorporation of the chosen flavours ({', '.join(config.story_flavours)})
        
        Output as structured JSON with this format:
        {{
            "title": "Story Title",
            "pages": [
                {{
                    "page_number": 1,
                    "scene_summary": "...",
                    "key_emotions": ["...", "..."],
                    "character_actions": "...",
                    "story_notes": "..."
                }}
            ]
        }}
        """,
        agent=story_planner,
        expected_output="A structured JSON story outline with all pages planned"
    )
    
    # Task 2: Write the Story
    task_write_story = Task(
        description=f"""
        Using the story structure from the Story Planner, write engaging text for each page.
        
        Requirements:
        - Each page should be 2-4 sentences for {config.age_group}
        - Use age-appropriate vocabulary and sentence structure
        - Create vivid imagery that children can visualize
        - Maintain consistent character voices
        - Build suspense and emotional connection
        - Incorporate the story flavours naturally
        
        Output as JSON:
        {{
            "pages": [
                {{
                    "page_number": 1,
                    "text": "The actual story text for this page..."
                }}
            ]
        }}
        """,
        agent=story_writer,
        expected_output="Complete story text for all pages in JSON format",
        context=[task_plan_story]
    )
    
    # Task 3: Art Direction
    task_art_direction = Task(
        description=f"""
        Based on the story structure and written text, create comprehensive art direction 
        for each page's illustration.
        
        Define:
        1. Overall visual style (e.g., watercolor, digital painting, cartoon, realistic)
        2. Color palette and mood
        3. Character design notes for {config.main_character} and {', '.join(config.supporting_characters)}
        4. For each page:
           - Composition (what should be in frame)
           - Perspective and angle
           - Lighting and atmosphere
           - Key visual elements
           - Emotional tone to convey
        
        Ensure visual consistency across all pages while allowing for variety in scenes.
        
        Output as JSON:
        {{
            "overall_style": "...",
            "color_palette": ["...", "..."],
            "character_designs": {{"character_name": "design notes"}},
            "pages": [
                {{
                    "page_number": 1,
                    "composition": "...",
                    "perspective": "...",
                    "lighting": "...",
                    "key_elements": ["...", "..."],
                    "mood": "..."
                }}
            ]
        }}
        """,
        agent=art_director,
        expected_output="Complete art direction for all pages in JSON format",
        context=[task_plan_story, task_write_story]
    )
    
    # Task 4: Generate Image Prompts
    task_image_prompts = Task(
        description=f"""
        Create detailed, specific image generation prompts for each page based on:
        - Story text
        - Art direction
        - Overall style and consistency requirements
        
        Each prompt should:
        - Be 50-100 words of detailed description
        - Start with the overall style
        - Describe the scene composition
        - Include character details and actions
        - Specify mood, lighting, and atmosphere
        - Mention key visual elements
        - Include technical parameters (e.g., "high quality, detailed, children's book illustration")
        - Maintain visual consistency across all pages
        
        Output as JSON:
        {{
            "pages": [
                {{
                    "page_number": 1,
                    "prompt": "A detailed prompt for image generation..."
                }}
            ]
        }}
        """,
        agent=image_prompt_agent,
        expected_output="Image generation prompts for all pages in JSON format",
        context=[task_plan_story, task_write_story, task_art_direction]
    )
    
    return [task_plan_story, task_write_story, task_art_direction, task_image_prompts]
