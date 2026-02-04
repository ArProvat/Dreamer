import os
import asyncio
from typing import Dict, List, Any
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

class ImageGenerationService:
    def __init__(self, s3_manager, mongodb_manager):
        self.s3_manager = s3_manager
        self.db_manager = mongodb_manager
        
        # Initialize the new Gen AI Client
        self.client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        
    async def generate_page_image(
        self,
        book_id: str,
        page_number: int,
        prompt: str,
        negative_prompt: str,
        reference_page_numbers: List[int] = None,
        illustration_style: str = "watercolor"
    ) -> Dict[str, Any]:
        """Generate image using Gemini 3 Pro native multimodal generation"""
        try:
            print(f"   📸 Generating page {page_number}...")
            
            # 1. Prepare contents list (Text + Images)
            # In the new SDK, we pass everything in a single 'contents' list
            styled_prompt = f"{prompt}. Style: {illustration_style}. Negative: {negative_prompt}"
            contents = [styled_prompt]
            
            # 2. Add reference images to the multimodal prompt
            if reference_page_numbers:
                print(f"      Loading {len(reference_page_numbers)} references...")
                reference_image_bytes = await self.s3_manager.get_reference_images(
                    book_id, 
                    reference_page_numbers
                )
                for img_bytes in reference_image_bytes:
                    # Convert bytes to PIL for the SDK
                    contents.append(Image.open(BytesIO(img_bytes)))

            # 3. Set up the Generation Config for Images
            # Note: response_modalities must include 'IMAGE'
            config = types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio="3:4",  # Supported: "1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"
                    image_size="2K"      # Options: "1K", "2K", "4K"
                )
            )

            # 4. Generate Content (Native Gemini 3 Image Generation)
            response = self.client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=contents,
                config=config
            )

            # 5. Extract the image from the multimodal response
            generated_img_bytes = None
            for part in response.parts:
                if part.inline_data:
                    # Use the helper to get the PIL image from the part
                    img = part.as_image()
                    img_byte_arr = BytesIO()
                    img.save(img_byte_arr, format='JPEG', quality=95)
                    generated_img_bytes = img_byte_arr.getvalue()
                    break

            if not generated_img_bytes:
                raise Exception("Model returned text but no image part.")

            # 6. Upload to S3
            s3_url = await self.s3_manager.upload_page_image(
                book_id=book_id,
                page_num=page_number,
                file_content=generated_img_bytes,
                filename=f"page_{page_number}.jpeg",
                content_type="image/jpeg"
            )

            return {
                "page_number": page_number,
                "image_url": s3_url,
                "success": True,
                "reference_pages_used": reference_page_numbers or []
            }

        except Exception as e:
            print(f"      ❌ Error: {str(e)}")
            return {"page_number": page_number, "success": False, "error": str(e)}

    async def generate_all_book_images(
        self,
        book_id: str,
        prompt_data: Dict[str, Any],
        writing_data: Dict[str, Any],
        illustration_style: str
    ) -> Dict[int, Dict[str, Any]]:
        """Sequential generation to leverage character consistency"""
        pages = prompt_data.get("pages", [])
        image_results = {}

        for page_data in pages:
            page_num = page_data.get("page_number")
            if page_data.get("page_type") == "cover":
                continue

            ref_selection = page_data.get("reference_selection", {})
            ref_nums = ref_selection.get("reference_page_numbers", [])

            result = await self.generate_page_image(
                book_id=book_id,
                page_number=page_num,
                prompt=page_data.get("formatted_image_prompt", ""),
                negative_prompt=page_data.get("negative_prompt", ""),
                reference_page_numbers=ref_nums,
                illustration_style=illustration_style
            )
            image_results[page_num] = result
            
            # Small delay for rate limit compliance
            await asyncio.sleep(2)

        return image_results