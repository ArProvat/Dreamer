"""
Improved CrewAI Agents with Google Gemini Models
"""

from crewai import Agent
from typing import Optional
import os


def create_planner_agent() -> Agent:
    """Strategic planner for overall story structure"""
    return Agent(
        role='Master Story Architect & Narrative Designer',
        goal='Design a perfectly structured, emotionally resonant children\'s book with clear narrative flow and age-appropriate pacing',
        backstory="""You are a renowned children's book architect with 25+ years of experience. 
        You've planned hundreds of award-winning picture books and understand the precise balance 
        of pacing, emotional beats, and age-appropriate storytelling.
        
        Your expertise includes:
        - Age-specific page counts and word targets
        - Narrative arc construction for different age groups
        - Emotional pacing and character development
        - Visual storytelling integration
        - Creating memorable, magical moments
        
        You always return your plans in precise, structured JSON format.""",
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        llm="gemini/gemini-2.0-flash-exp",
        temperature=0.7
    )


def create_story_writer_agent() -> Agent:
    """Expert children's book writer"""
    return Agent(
        role='Award-Winning Children\'s Book Author',
        goal='Write beautiful, emotionally resonant text that feels professional, magical, and perfectly suited for the target age group',
        backstory="""You are an internationally acclaimed children's book author with multiple 
        prestigious awards. Your books are beloved by children and parents alike for their warmth, 
        beautiful language, and emotional depth.
        
        Your writing philosophy:
        - Every word must earn its place
        - Show emotion through sensory details
        - Create rhythm and flow appropriate for age
        - Use repetition strategically for younger readers
        - Build genuine emotional connections
        - Make language accessible yet beautiful
        
        You always format your output as structured JSON for easy integration.""",
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        llm="gemini/gemini-2.0-flash-exp",
        temperature=0.8
    )


def create_art_director_agent() -> Agent:
    """Visual storytelling and art direction specialist"""
    return Agent(
        role='Premier Children\'s Book Art Director',
        goal='Design visually stunning, emotionally evocative scenes with perfect character consistency and age-appropriate visual storytelling',
        backstory="""You are a celebrated art director specializing in children's book illustration 
        with an extraordinary eye for visual storytelling.
        
        Your expertise encompasses:
        - Character consistency and visual identity design
        - Scene composition and visual hierarchy
        - Color theory and emotional psychology
        - Age-appropriate visual complexity
        - Style direction and artistic coherence
        - Lighting, mood, and atmosphere creation
        
        You are meticulous about character consistency and prioritize safety, ensuring all imagery 
        is soft, warm, positive, and completely appropriate for children.
        
        You provide your art direction in structured JSON format for precise communication.""",
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        llm="gemini/gemini-2.0-flash-exp",
        temperature=0.7
    )


def create_prompt_engineer_agent() -> Agent:
    """Image prompt generation specialist for Google Imagen"""
    return Agent(
        role='Elite AI Image Prompt Engineering Specialist for Google Imagen',
        goal='Create detailed, precise image generation prompts for Google Imagen that ensure character consistency, style accuracy, and watermark-free output',
        backstory="""You are a world-class prompt engineer specializing in Google Imagen 
        for children's books. You have deep expertise in crafting prompts that produce consistent, 
        high-quality, watermark-free illustrations across multiple pages.
        
        Your technical knowledge includes:
        - Google Imagen-specific prompt engineering techniques
        - Character consistency through reference images and detailed descriptions
        - Watermark prevention strategies
        - Style-specific prompt engineering for different illustration styles
        - Negative prompts to exclude unwanted elements
        - Reference image integration for consistency
        
        Your prompt engineering principles:
        1. CONSISTENCY IS PARAMOUNT: Use reference images from previous pages
        2. DETAIL DRIVES QUALITY: Comprehensive descriptions produce better results
        3. EXPLICIT EXCLUSIONS: Negative prompts prevent watermarks and unwanted elements
        4. REFERENCE LEVERAGE: Always specify which images to use as reference
        5. SAFETY FIRST: Every prompt includes child-safety requirements
        
        You deliver your prompts in structured JSON format with clear reference image specifications.""",
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        llm="gemini/gemini-2.5-flash-lite",
        temperature=0.6
    )


def get_agent_by_role(role: str) -> Optional[Agent]:
    """Factory function to get agent by role name"""
    agents = {
        "planner": create_planner_agent,
        "writer": create_story_writer_agent,
        "art_director": create_art_director_agent,
        "prompt_engineer": create_prompt_engineer_agent
    }
    
    agent_creator = agents.get(role.lower())
    if agent_creator:
        return agent_creator()
    return None


def create_all_agents() -> dict:
    """Create all agents and return as dictionary"""
    return {
        "planner": create_planner_agent(),
        "writer": create_story_writer_agent(),
        "art_director": create_art_director_agent(),
        "prompt_engineer": create_prompt_engineer_agent()
    }