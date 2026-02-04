# services/image_generator.py
import google.generativeai as genai
from typing import Dict, List, Any
import asyncio
from PIL import Image
from io import BytesIO
import base64
import os

class ImageGenerationService:
    def __init__(self, s3_manager, mongodb_manager):
        self.s3_manager = s3_manager
        self.db_manager = mongodb_manager
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
    async def generate_page_image(
        self,
        book_id: str,
        page_number: int,
        prompt: str,
        negative_prompt: str,
        reference_page_numbers: List[int] = None,
        illustration_style: str = "watercolor"
    ) -> Dict[str, Any]:
        """Generate image for a single page with reference images"""
        try:
            print(f"   📸 Generating page {page_number}...")
            
            # Get reference images from S3 if specified
            reference_images = []
            if reference_page_numbers and len(reference_page_numbers) > 0:
                print(f"      Loading {len(reference_page_numbers)} reference images from S3...")
                reference_image_bytes = await self.s3_manager.get_reference_images(
                    book_id, 
                    reference_page_numbers
                )
                
                # Convert bytes to PIL Images for Imagen
                for img_bytes in reference_image_bytes:
                    img = Image.open(BytesIO(img_bytes))
                    reference_images.append(img)
                
                print(f"      ✓ Loaded {len(reference_images)} reference images")
            
            # Configure Imagen model
            model = genai.ImageGenerationModel("imagen-3.0-generate-001")
            
            # Build generation parameters
            generation_params = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "number_of_images": 1,
                "aspect_ratio": "3:4",  # Portrait for children's books
                "safety_filter_level": "block_some",
                "person_generation": "allow_adult"
            }
            
            # Add reference images if available
            if reference_images:
                generation_params["reference_images"] = reference_images
                generation_params["style_reference_weight"] = 0.7  # Balance between prompt and references
            
            # Generate image
            response = model.generate_images(**generation_params)
            
            if not response.images:
                raise Exception("No images generated")
            
            # Get the generated image
            generated_image = response.images[0]
            
            # Convert to bytes
            img_byte_arr = BytesIO()
            generated_image._pil_image.save(img_byte_arr, format='JPEG', quality=95)
            img_bytes = img_byte_arr.getvalue()
            
            # Upload to S3
            s3_url = await self.s3_manager.upload_page_image(
                book_id=book_id,
                page_num=page_number,
                file_content=img_bytes,
                filename=f"page_{page_number}.jpeg",
                content_type="image/jpeg"
            )
            
            print(f"      ✓ Page {page_number} generated and uploaded")
            
            return {
                "page_number": page_number,
                "image_url": s3_url,
                "success": True,
                "reference_pages_used": reference_page_numbers or []
            }
            
        except Exception as e:
            print(f"      ❌ Error generating page {page_number}: {str(e)}")
            return {
                "page_number": page_number,
                "image_url": None,
                "success": False,
                "error": str(e),
                "reference_pages_used": reference_page_numbers or []
            }
    
    async def generate_all_book_images(
        self,
        book_id: str,
        prompt_data: Dict[str, Any],
        writing_data: Dict[str, Any],
        illustration_style: str
    ) -> Dict[int, Dict[str, Any]]:
        """Generate all images for the book sequentially"""
        try:
            print(f"\n🎨 Generating all book images...")
            
            pages = prompt_data.get("pages", [])
            image_results = {}
            
            # Generate images sequentially (important for reference consistency)
            for page_data in pages:
                page_num = page_data.get("page_number")
                
                # Skip cover if it's just text
                if page_data.get("page_type") == "cover":
                    print(f"   ⏭️  Skipping cover page {page_num}")
                    continue
                
                # Get reference page numbers
                reference_selection = page_data.get("reference_selection", {})
                reference_page_numbers = reference_selection.get("reference_page_numbers", [])
                
                # Generate the image
                result = await self.generate_page_image(
                    book_id=book_id,
                    page_number=page_num,
                    prompt=page_data.get("formatted_image_prompt", ""),
                    negative_prompt=page_data.get("negative_prompt", ""),
                    reference_page_numbers=reference_page_numbers,
                    illustration_style=illustration_style
                )
                
                image_results[page_num] = result
                
                # Small delay to avoid rate limits
                await asyncio.sleep(2)
            
            print(f"   ✓ All {len(image_results)} images generated")
            
            return image_results
            
        except Exception as e:
            print(f"   ❌ Error in batch generation: {str(e)}")
            raise