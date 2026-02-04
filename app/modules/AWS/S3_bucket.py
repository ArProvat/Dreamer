import boto3
from botocore.exceptions import ClientError
import uuid
from typing import List
import httpx
from io import BytesIO

class S3Manager:
    def __init__(self, aws_access_key: str, aws_secret_key: str, bucket_name: str, region: str = 'us-east-1'):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        self.bucket_name = bucket_name
        
    async def upload_page_image(
        self, 
        book_id: str, 
        page_num: int, 
        file_content: bytes, 
        filename: str, 
        content_type: str = 'image/jpeg'
    ) -> str:
        """Upload page image to S3"""
        try:
            file_extension = filename.split('.')[-1]
            unique_filename = f'{book_id}/page_{page_num}.{file_extension}'

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_content,  # ✅ Fixed typo
                ContentType=content_type
            )
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{unique_filename}"
            return url
        except ClientError as e:
            raise Exception(f"Failed to upload image: {str(e)}")
        
    async def upload_character_image(
        self, 
        file_content: bytes, 
        filename: str, 
        content_type: str = 'image/jpeg'
    ) -> str:
        """Upload character image to S3"""
        try:
            file_extension = filename.split('.')[-1]
            unique_filename = f"character_images/{uuid.uuid4()}.{file_extension}"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_content,
                ContentType=content_type
            )
            
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{unique_filename}"
            return url
        except ClientError as e:
            raise Exception(f"Failed to upload image: {str(e)}")
    
    async def upload_multiple_character_images(self, files: List[tuple]) -> List[str]:
        """Upload multiple character images"""
        urls = []
        for file_content, filename, content_type in files:
            url = await self.upload_character_image(file_content, filename, content_type)
            urls.append(url)
        return urls
    
    async def download_image(self, s3_url: str) -> bytes:
        """Download image from S3 URL"""
        try:
            # Extract key from URL
            # https://bucket-name.s3.amazonaws.com/path/to/file.jpg
            key = s3_url.split('.s3.amazonaws.com/')[-1]
            
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"Failed to download image from S3: {str(e)}")
    
    async def get_reference_images(self, book_id: str, page_numbers: List[int]) -> List[bytes]:
        """Get reference images for specific pages"""
        try:
            reference_images = []
            for page_num in page_numbers:
                key = f"{book_id}/page_{page_num}.jpeg"
                
                try:
                    response = self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=key
                    )
                    reference_images.append(response['Body'].read())
                except ClientError as e:
                    print(f"⚠️  Could not find reference image for page {page_num}: {str(e)}")
                    continue
            
            return reference_images
        except Exception as e:
            raise Exception(f"Failed to get reference images: {str(e)}")