from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException, status
from app.core.config import settings
import io
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

# Initialize MinIO client
minio_client = Minio(
    f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_USE_SSL
)

async def upload_file(file_data: bytes, file_name: str, content_type: str) -> str:
    """
    Upload file to MinIO storage
    
    Args:
        file_data: File bytes
        file_name: Name of the file
        content_type: MIME type of the file
    
    Returns:
        str: Presigned URL of the uploaded file (valid for 7 days)
    """
    try:
        # Upload file
        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=file_name,
            data=io.BytesIO(file_data),
            length=len(file_data),
            content_type=content_type
        )
        
        # Generate presigned URL valid for 7 days
        url = minio_client.presigned_get_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=file_name,
            expires=timedelta(days=7)
        )
        
        logger.info(f"File uploaded successfully: {file_name}")
        return url
    
    except S3Error as e:
        logger.error(f"MinIO error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

async def delete_file(file_name: str) -> None:
    """
    Delete file from MinIO storage
    
    Args:
        file_name: Name of the file to delete
    """
    try:
        minio_client.remove_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=file_name
        )
    except S3Error as e:
        logger.error(f"Failed to delete file {file_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )
