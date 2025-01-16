from datetime import datetime, timedelta
from typing import Optional
from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error
import os
from app.core.config import settings

# Create Minio client
client = Minio(
    endpoint=f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_USE_SSL
)

async def ensure_bucket(bucket_name: str):
    """Ensure bucket exists"""
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
    except S3Error as e:
        raise Exception(f"Minio error: {e}")

async def upload_file(
    file: UploadFile,
    folder: str,
    filename: Optional[str] = None,
    bucket: str = settings.MINIO_BUCKET_NAME
) -> str:
    """
    Upload file to Minio
    
    Args:
        file: File to upload
        folder: Storage folder
        filename: Custom filename (optional)
        bucket: Bucket name
    
    Returns:
        str: File access URL
    """
    try:
        # Ensure bucket exists
        await ensure_bucket(bucket)
        
        # Generate filename
        if not filename:
            ext = os.path.splitext(file.filename)[1]
            filename = f"{int(datetime.now().timestamp())}{ext}"
        
        # Complete object name (including folder)
        object_name = f"{folder}/{filename}"
        
        # Upload file
        content_type = file.content_type or "application/octet-stream"
        result = client.put_object(
            bucket_name=bucket,
            object_name=object_name,
            data=file.file,
            length=-1,  # Let Minio calculate file size
            content_type=content_type
        )
        
        # Generate presigned URL
        url = client.presigned_get_object(
            bucket_name=bucket,
            object_name=object_name,
            expires=timedelta(days=7)
        )
        
        return url
        
    except S3Error as e:
        raise Exception(f"Failed to upload file: {e}")

async def delete_file(
    file_path: str,
    bucket: str = settings.MINIO_BUCKET_NAME
) -> bool:
    """
    Delete file from Minio
    
    Args:
        file_path: File path (folder/filename)
        bucket: Bucket name
    
    Returns:
        bool: Whether deletion was successful
    """
    try:
        client.remove_object(bucket, file_path)
        return True
    except S3Error as e:
        raise Exception(f"Failed to delete file: {e}")

async def get_file_url(
    file_path: str,
    bucket: str = settings.MINIO_BUCKET_NAME,
    expires: timedelta = timedelta(hours=1)
) -> str:
    """
    Get presigned URL for file
    
    Args:
        file_path: File path
        bucket: Bucket name
        expires: URL expiration time
    
    Returns:
        str: Presigned URL
    """
    try:
        url = client.presigned_get_object(
            bucket_name=bucket,
            object_name=file_path,
            expires=expires
        )
        return url
    except S3Error as e:
        raise Exception(f"Failed to get file URL: {e}")
