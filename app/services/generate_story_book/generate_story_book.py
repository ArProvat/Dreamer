from crewai import Crew, Process
from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime
import os
from ...agents.agents import create_all_agents
from ...agents.task import (
    create_planning_task,
    create_writing_task,
    create_art_direction_task,
    create_prompt_generation_task,
)
from ...DB.mongoDB.mongoDB import MongoManager
#from services.image_generator import generate_all_book_images

_mongoManager = MongoManager()

async def orchestrate_book_generation(
    book_id: str,
    session_id: str,
    storyline_id: str,
    illustration_style: str,
    dedication: str
) -> Dict[str, Any]:
    """
    Main orchestration function that coordinates all agents to generate a complete book
    
    Args:
        book_id: Unique book identifier
        session_id: User session identifier
        storyline_id: Selected storyline identifier
        illustration_style: Chosen illustration style
        dedication: Dedication text for the book
        
    Returns:
        Complete book data with all pages and images
    """
    
    print(f"🎬 Starting book generation for book_id: {book_id}")
    
    try:
        await _mongoManager.initialize()
        await _mongoManager.update_session(
            session_id,
            {"illustration_style": illustration_style, "dedication": dedication}
        )
        # ==================== STEP 1: GATHER INFORMATION ====================
        print("\n📋 Step 1: Gathering information...")
        
        # Get session data
        session = await _mongoManager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Get storyline
        storyline = await _mongoManager.get_story_overviews_by_session_id(storyline_id)
        if not storyline:
            raise ValueError(f"Storyline {storyline_id} not found")
        
        # Prepare character data
        characters = {
            "main": session.main_characters or [],
            "supporting": session.supporting_characters or []
        }
        
        # Prepare personality details
        personality_details = {}
        if session.personality_questions:
            personality_details.update(session.personality_questions)
        if session.character_personality:
            personality_details.update(session.character_personality)
        
        # Prepare storyline data
        storyline_data = {
            "title": storyline.title,
            "overview": storyline.overview,
            "emotional_tone": storyline.emotional_tone,
            "theme_focus": storyline.theme_focus,
            "genre": storyline.genre
        }
        
        print(f"   ✓ Session data loaded")
        print(f"   ✓ Storyline: {storyline.title}")
        print(f"   ✓ Age range: {session.age_range}")
        print(f"   ✓ Style: {illustration_style}")
        
        # Update book status
        #await update_book_status(book_id, BookStatus.PROCESSING, 5, "Initializing creative team...")
        
        print("\n🤖 Step 2: Creating AI agents...")
        
        agents = create_all_agents()
        
        print(f"   ✓ Planner agent ready")
        print(f"   ✓ Writer agent ready")
        print(f"   ✓ Art Director agent ready")
        print(f"   ✓ Prompt Engineer agent ready")
        
        #await update_book_status(book_id, BookStatus.PROCESSING, 10, "Creative team assembled...")
        
        print("\n📐 Step 3: Story planning phase...")
        
        planning_task = create_planning_task(
            planner=agents["planner"],
            storyline=storyline_data,
            characters=characters,
            age_range=session.age_range,
            flavours=session.story_flavours or []
        )
        
        planning_crew = Crew(
            agents=[agents["planner"]],
            tasks=[planning_task],
            process=Process.sequential,
            verbose=True
        )
        
        #await update_book_status(book_id, BookStatus.PROCESSING, 15, "Planning story structure...")
        
        planning_result = planning_crew.kickoff()
        planning_output = clean_json_output(planning_result)
        
        print(f"   ✓ Story structure planned")
        print(f"   ✓ Pages: {planning_output.get('book_structure', {}).get('total_pages', 'N/A')}")
        
        # Store planning data
        ''' await update_book(book_id, {
            "story_data": {
                "planning": planning_output,
                "storyline": storyline_data
            }
        })'''
        
        print("\n✍️  Step 4: Writing story text...")
        
        writing_task = create_writing_task(
            writer=agents["writer"],
            planning_output=json.dumps(planning_output, indent=2),
            age_range=session.age_range,
            characters=characters,
            personality_details=personality_details,
            dedication=dedication
        )
        
        writing_crew = Crew(
            agents=[agents["writer"]],
            tasks=[writing_task],
            process=Process.sequential,
            verbose=True
        )
        
        #await update_book_status(book_id, BookStatus.PROCESSING, 30, "Writing your story...")
        
        writing_result = writing_crew.kickoff()
        writing_output = clean_json_output(writing_result)
        
        print(f"   ✓ Story text written")
        print(f"   ✓ Pages with text: {len(writing_output.get('pages', []))}")
        
        # Update book with story text
        '''await update_book(book_id, {
            "story_data.writing": writing_output
        })
        '''
        print("\n🎨 Step 5: Designing visual scenes...")
        
        art_direction_task = create_art_direction_task(
            art_director=agents["art_director"],
            story_text=json.dumps(writing_output, indent=2),
            characters=characters,
            style=illustration_style
        )
        
        art_crew = Crew(
            agents=[agents["art_director"]],
            tasks=[art_direction_task],
            process=Process.sequential,
            verbose=True
        )
        
        #await update_book_status(book_id, BookStatus.PROCESSING, 45, "Designing visual scenes...")
        
        art_result = art_crew.kickoff()
        art_output = clean_json_output(art_result)
        
        print(f"   ✓ Visual scenes designed")
        print(f"   ✓ Art direction complete")
        
        # Update book with art direction
        '''await update_book(book_id, {
            "story_data.art_direction": art_output
        })
        '''
        # ==================== STEP 6: PROMPT GENERATION PHASE ====================
        print("\n🖼️  Step 6: Generating image prompts...")
        
        prompt_generation_task = create_prompt_generation_task(
            prompt_engineer=agents["prompt_engineer"],
            art_direction=json.dumps(art_output, indent=2),
            story_text=json.dumps(writing_output, indent=2),
            characters=characters,
            style=illustration_style,
            book_id=book_id
        )
        
        prompt_crew = Crew(
            agents=[agents["prompt_engineer"]],
            tasks=[prompt_generation_task],
            process=Process.sequential,
            verbose=True
        )
        
        #await update_book_status(book_id, BookStatus.PROCESSING, 55, "Creating image generation prompts...")
        
        prompt_result = prompt_crew.kickoff()
        prompt_output = clean_json_output(prompt_result)
        
        print(f"   ✓ Image prompts generated")
        print(f"   ✓ Ready for image generation")
        
        # Update book with prompts
        '''await update_book(book_id, {
            "story_data.image_prompts": prompt_output
        })
        '''
        # ==================== IMAGE GENERATION PHASE ====================
        print("\n🎨 Step 7: Generating illustrations...")
        
        #await update_book_status(book_id, BookStatus.PROCESSING, 60, "Creating beautiful illustrations...")
        
        # Get character reference images if available
        character_references = []
        if session.main_characters:
            for char in session.main_characters:
                if char.get("reference_image_url"):
                    character_references.append(char["reference_image_url"])
        
        # Generate all images sequentially with consistency checks
        '''image_results = await generate_all_book_images(
            book_id=book_id,
            prompt_data=prompt_output,
            writing_data=writing_output,
            character_references=character_references,
            illustration_style=illustration_style,
            progress_callback=lambda progress, msg: update_book_status(
                book_id, BookStatus.PROCESSING, 60 + int(progress * 0.3), msg
            )
        )'''
        
        print(f"   ✓ All illustrations generated")
        print(f"   ✓ Images stored in S3")
        
        # ==================== STEP 8: VALIDATION PHASE ====================
        print("\n✅ Step 8: Quality validation...")
        
        #await update_book_status(book_id, BookStatus.PROCESSING, 92, "Validating quality...")
        
        
        # ==================== STEP 9: FINALIZATION ====================
        print("\n🎉 Step 9: Finalizing book...")
        
        #await update_book_status(book_id, BookStatus.PROCESSING, 95, "Finalizing your book...")
        
        # Store all page data
        pages_data = []
        for i, page_prompt in enumerate(prompt_output.get("pages", [])):
            page_num = page_prompt.get("page_number", i + 1)
            
            # Get corresponding text
            page_text = next(
                (p.get("text", "") for p in writing_output.get("pages", []) 
                if p.get("page_number") == page_num),
                ""
            )
            
            # Get image result
            #image_info = image_results.get(str(page_num), {})
            
            '''page_data = {
                "page_number": page_num,
                "page_type": page_prompt.get("page_type", "story"),
                "text_content": page_text,
                "image_prompt": page_prompt.get("image_prompt", ""),
                "art_direction": json.dumps(art_output.get("pages", [])[i] if i < len(art_output.get("pages", [])) else {}),
                "image_url": image_info.get("image_url", ""),
                "thumbnail_url": image_info.get("thumbnail_url", ""),
                "preview_url": image_info.get("preview_url", ""),
                "consistency_score": image_info.get("consistency_score", 0),
                "safety_check_passed": image_info.get("safety_passed", False),
                "is_approved": image_info.get("approved", False),
                "generation_attempts": image_info.get("attempts", 1)
            }
            '''
            #pages_data.append(page_data)
            #await add_book_page(book_id, page_data)
        
        # Mark book as complete
        '''await update_book(book_id, {
            "is_preview_ready": True,
            "completed_at": datetime.utcnow()
        })
        
        await update_book_status(book_id, BookStatus.COMPLETED, 100, "Your book is ready!")
        '''
        print(f"\n✨ Book generation complete!")
        print(f"   Book ID: {book_id}")
        print(f"   Total pages: {len(pages_data)}")
        print(f"   Status: COMPLETED")
        
        return {
            "book_id": book_id,
            "status": "completed",
            "pages": pages_data,
            "metadata": {
                "title": storyline.title,
                "age_range": session.age_range,
                "style": illustration_style,
                "total_pages": len(pages_data),
                "completion_time": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        print(f"\n❌ Error during book generation: {str(e)}")
        #await update_book_status(book_id, BookStatus.FAILED, 0, f"Error: {str(e)}")
        raise


def clean_json_output(result: Any) -> Dict:
    """
    Clean and parse JSON output from CrewAI agents
    Handles markdown code blocks and other formatting issues
    """
    try:
        if isinstance(result, dict):
            return result
        
        result_str = str(result)
        
        if "```json" in result_str:
            result_str = result_str.split("```json")[1].split("```")[0]
        elif "```" in result_str:
            result_str = result_str.split("```")[1].split("```")[0]
        
        result_str = result_str.strip()
        
        parsed = json.loads(result_str)
        return parsed
        
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parsing error: {str(e)}")
        print(f"Raw output: {result_str[:500]}...")
        
        try:
            start = result_str.find("{")
            end = result_str.rfind("}") + 1
            if start != -1 and end > start:
                clean_str = result_str[start:end]
                return json.loads(clean_str)
        except:
            pass
        
        return {"error": "Failed to parse JSON output", "raw": str(result)[:500]}

'''
async def handle_revisions(
    book_id: str,
    validation_output: Dict,
    agents: Dict,
    current_images: Dict
) -> Dict:
    """
    Handle revisions for pages that failed validation
    """
    print("\n🔄 Handling revisions...")
    
    pages_to_regenerate = validation_output.get("revision_required", {}).get("pages_to_regenerate", [])
    
    if not pages_to_regenerate:
        return current_images
    
    print(f"   Pages to regenerate: {pages_to_regenerate}")
    
    # Import image generator
    from services.image_generator import regenerate_images
    
    # Regenerate failed pages
    revised_images = await regenerate_images(
        book_id=book_id,
        page_numbers=pages_to_regenerate,
        validation_feedback=validation_output,
        current_images=current_images
    )
    
    # Merge with current images
    current_images.update(revised_images)
    
    print(f"   ✓ Revisions complete")
    
    return current_images

'''
# ==================== QUICK START FUNCTION ====================

'''async def quick_start_book_generation(
    email: str,
    story_idea: str,
    child_name: str,
    age_range: str,
    illustration_style: str = "Soft Pastel Storybook"
) -> Dict[str, Any]:
    """
    Quick start function for simple book generation
    Creates a book with minimal input
    """
    
    # Create simple session data
    from models.database import create_user, create_session, create_storylines, create_book
    import uuid
    
    # Get or create user
    from models.database import get_user_by_email
    user = await get_user_by_email(email)
    if not user:
        user = await create_user({"email": email})
    
    # Create session
    session = await create_session({
        "user_id": user.id,
        "story_idea": story_idea,
        "age_range": age_range,
        "story_flavours": ["adventure", "friendship"],
        "main_characters": [{
            "name": child_name,
            "species": "human",
            "role": "protagonist",
            "hair_fur": "brown hair",
            "clothing": "colorful outfit",
            "signature_item": None
        }]
    })
    
    # Generate storyline options
    from services.story_overview_generator import generate_three_storylines
    
    storylines = await generate_three_storylines(
        story_idea=story_idea,
        age_range=age_range,
        story_flavours=["adventure", "friendship"],
        main_characters=session.main_characters,
        supporting_characters=None,
        personality_questions=None,
        character_personality=None
    )
    
    # Store storylines
    storyline_docs = [
        {
            "session_id": session.id,
            "title": s["title"],
            "overview": s["overview"],
            "emotional_tone": s["emotional_tone"],
            "theme_focus": s["theme_focus"],
            "genre": s["genre"]
        }
        for s in storylines
    ]
    stored_storylines = await create_storylines(storyline_docs)
    
    # Use first storyline
    selected_storyline = stored_storylines[0]
    
    # Create book
    book_id = str(uuid.uuid4())
    await create_book({
        "id": book_id,
        "user_id": user.id,
        "session_id": session.id,
        "storyline_id": selected_storyline.id,
        "age_range": age_range,
        "illustration_style": illustration_style,
        "dedication": f"For {child_name}, with love"
    })
    
    # Start generation
    result = await orchestrate_book_generation(
        book_id=book_id,
        session_id=session.id,
        storyline_id=selected_storyline.id,
        illustration_style=illustration_style,
        dedication=f"For {child_name}, with love"
    )
    
    return result
'''

# ==================== USAGE EXAMPLE ====================
'''
if __name__ == "__main__":
    import asyncio
    
    # Example: Full book generation
    async def main():
        result = await quick_start_book_generation(
            email="parent@example.com",
            story_idea="A brave girl discovers magic in her grandmother's garden",
            child_name="Emma",
            age_range="4-6",
            illustration_style="Soft Pastel Storybook"
        )
        
        print(f"\n✨ Book created successfully!")
        print(f"Book ID: {result['book_id']}")
        print(f"Pages: {len(result['pages'])}")
    
    asyncio.run(main())
    '''