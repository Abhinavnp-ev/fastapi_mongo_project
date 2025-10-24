from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from fastapi import UploadFile, HTTPException
from .config import settings
import uuid
from datetime import datetime
import os


class GCSService:
    def __init__(self):
        if settings.GCS_CREDENTIALS_PATH and os.path.exists(settings.GCS_CREDENTIALS_PATH):
            self.client = storage.Client.from_service_account_json(settings.GCS_CREDENTIALS_PATH)
        else:
            # Uses Application Default Credentials (Cloud Run service account)
            self.client = storage.Client()
        self.bucket = self.client.bucket(settings.GCS_BUCKET_NAME)
    
    async def upload_file(self, file: UploadFile) -> dict:
        """
        Upload file to Google Cloud Storage and return metadata
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            dict: File metadata including URL, name, size, type
        """
        try:
            # Generate unique filename to avoid collisions
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create blob (file object in GCS)
            blob = self.bucket.blob(unique_filename)
            
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Upload to GCS
            blob.upload_from_string(
                file_content,
                content_type=file.content_type or 'application/octet-stream'
            )
            
            # Make the blob publicly accessible (optional, for development)
            # blob.make_public()
            
            # Generate public URL
            file_url = blob.public_url
            
            # Return metadata
            return {
                "url": file_url,
                "filename": file.filename,
                "unique_filename": unique_filename,
                "size": file_size,
                "content_type": file.content_type or 'application/octet-stream',
                "uploaded_at": datetime.utcnow()
            }
            
        except GoogleCloudError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to GCS: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error during file upload: {str(e)}"
            )
# Create singleton instance
gcs_service = GCSService()