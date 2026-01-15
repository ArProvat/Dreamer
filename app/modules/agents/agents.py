from crewai import Agent, Task, Crew, Process

def create_agents(config: StoryConfig,llm):
    
    # Agent 1: Story Planner
    story_planner = Agent(
        role='Story Planner',
        goal=f'Create a detailed {config.num_pages}-page story outline for {config.age_group} featuring {config.main_character}',
        backstory=f"""You are an experienced children's book author who specializes in 
        creating engaging stories for {config.age_group}. You excel at story structure, 
        pacing, and incorporating themes of {', '.join(config.story_flavours)}. 
        You understand child psychology and age-appropriate content.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    # Agent 2: Story Writer
    story_writer = Agent(
        role='Story Writer',
        goal=f'Write compelling, age-appropriate text for each page that brings the story to life',
        backstory=f"""You are a talented children's book writer with a gift for 
        creating vivid, engaging prose for {config.age_group}. You know how to 
        balance description with action, and you write with warmth and clarity. 
        Each page you write should be self-contained yet flow naturally into the next.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    # Agent 3: Art Director
    art_director = Agent(
        role='Art Director',
        goal='Define the visual style, composition, and artistic direction for each illustration',
        backstory="""You are an experienced art director for children's books. You understand 
        color theory, composition, and how to create illustrations that appeal to children 
        while supporting the story narrative. You think about visual consistency across pages 
        and emotional impact of imagery.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    # Agent 4: Image Prompt Agent
    image_prompt_agent = Agent(
        role='Image Prompt Engineer',
        goal='Create detailed, specific prompts for AI image generation that match the art direction',
        backstory="""You are an expert at crafting prompts for AI image generation systems. 
        You know how to be specific about style, composition, lighting, mood, and details. 
        You understand how to maintain visual consistency across multiple images and create 
        prompts that produce high-quality, story-appropriate illustrations for children's books.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return story_planner, story_writer, art_director, image_prompt_agent