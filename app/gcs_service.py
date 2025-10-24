from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from fastapi import UploadFile, HTTPException
from .config import settings
import uuid
from datetime import datetime,timedelta
import os


class GCSService:
    def __init__(self):
        if settings.GCS_CREDENTIALS_PATH and os.path.exists(settings.GCS_CREDENTIALS_PATH):
            self.client = storage.Client.from_service_account_json(settings.GCS_CREDENTIALS_PATH)
        else:
            
            self.client = storage.Client()
        self.bucket = self.client.bucket(settings.GCS_BUCKET_NAME)

    async def upload_file(self, file: UploadFile) -> dict:
        try:
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"

            blob = self.bucket.blob(unique_filename)

            
            with blob.open("wb") as f:
                while True:
                    chunk = await file.read(1024 * 1024)  
                    if not chunk:
                        break
                    f.write(chunk)

            file_url = blob.public_url
            file_size = blob.size  

            return {
                "url": file_url,
                "filename": file.filename,
                "unique_filename": unique_filename,
                "size": file_size,
                "content_type": file.content_type or 'application/octet-stream',
                "uploaded_at": datetime.utcnow(),
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
    def generate_upload_signed_url(self, filename: str, expiration_minutes: int = 15) -> str:
        blob = self.bucket.blob(filename)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="PUT",
            content_type="application/octet-stream"
        )
        return url
# Create singleton instance
gcs_service = GCSService()