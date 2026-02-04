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
from ..image_genertor.image_generation import ImageGenerationService
from ...modules.AWS.S3_bucket import S3Manager
_mongoManager = MongoManager()


async def orchestrate_book_generation(
    book_id: str,
    session_id: str,
    storyline_id: str,
    illustration_style: str,
    dedication: str
) -> Dict[str, Any]:
    """Main orchestration function"""
    
    print(f"🎬 Starting book generation for book_id: {book_id}")
    
    try:
        await _mongoManager.initialize()
        
        # ✅ Create the book record first
        await _mongoManager.create_book({
            "_id": book_id,
            "session_id": session_id,
            "book_title": "",  # Will be updated with storyline title
            "page_ids": [],
            "status": "generating",
            "created_at": datetime.utcnow()
        })
        
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
                
        planning_result = planning_crew.kickoff()
        planning_output = clean_json_output(planning_result)
        
        print(f"   ✓ Story structure planned")
        print(f"   ✓ Pages: {planning_output.get('book_structure', {}).get('total_pages', 'N/A')}")
        
        # Store planning data
        await _mongoManager.update_book(book_id, {
            "story_data": {
                "planning": planning_output,
                "storyline": storyline_data
            }
        })
        
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
        
        
        writing_result = writing_crew.kickoff()
        writing_output = clean_json_output(writing_result)
        
        print(f"   ✓ Story text written")
        print(f"   ✓ Pages with text: {len(writing_output.get('pages', []))}")
        
        # Update book with story text
        await _mongoManager.update_book(book_id, {
            "story_data.writing": writing_output
        })
        
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
        
        
        art_result = art_crew.kickoff()
        art_output = clean_json_output(art_result)
        
        print(f"   ✓ Visual scenes designed")
        print(f"   ✓ Art direction complete")
        
        # Update book with art direction
        await _mongoManager.update_book(book_id, {
            "story_data.art_direction": art_output
        })
        
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
        
        # Initialize image generation service
        s3_manager = S3Manager(
            aws_access_key=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_key=os.getenv('AWS_SECRET_KEY'),
            bucket_name=os.getenv('S3_BUCKET_NAME')
        )
        
        image_service = ImageGenerationService(s3_manager, _mongoManager)
        
        # Generate all images with reference support
        image_results = await image_service.generate_all_book_images(
            book_id=book_id,
            prompt_data=prompt_output,
            writing_data=writing_output,
            illustration_style=illustration_style
        )
        
        print(f"   ✓ All illustrations generated")
        
        # ==================== STORE PAGE DATA ====================
        print("\n💾 Step 8: Storing page data...")
        
        pages_data = []
        page_ids = []
        
        # ✅ Fixed: Store ALL pages, not just the last one
        for i, page_prompt in enumerate(prompt_output.get("pages", [])):
            page_num = page_prompt.get("page_number", i + 1)
            
            # Get corresponding text
            page_text = next(
                (p.get("text", "") for p in writing_output.get("pages", []) 
                if p.get("page_number") == page_num),
                ""
            )
            
            # Get image result
            image_info = image_results.get(page_num, {})
            
            # Get art direction for this page
            art_pages = art_output.get("pages", [])
            art_direction = art_pages[i] if i < len(art_pages) else {}
            
            page_data = {
                "book_id": book_id,
                "session_id": session_id,
                "page_number": page_num,
                "page_type": page_prompt.get("page_type", "story"),
                "text_content": page_text,
                "image_prompt": page_prompt.get("formatted_image_prompt", ""),
                "art_direction": json.dumps(art_direction),
                "image_url": image_info.get("image_url", ""),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Add page to MongoDB
            page_id = await _mongoManager.add_book_page(book_id, page_data)
            page_ids.append(page_id)
            pages_data.append(page_data)
            
            print(f"   ✓ Stored page {page_num}")
        
        # Update book with all page IDs and title
        await _mongoManager.update_book(book_id, {
            "page_ids": page_ids,
            "book_title": storyline.title,
            "status": "completed",
            "is_preview_ready": True,
            "completed_at": datetime.utcnow()
        })
        
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
        # Update book status to failed
        await _mongoManager.update_book(book_id, {
            "status": "failed",
            "error": str(e)
        })
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
