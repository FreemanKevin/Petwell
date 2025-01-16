from fastapi import HTTPException, status, UploadFile
import imghdr
from typing import Tuple
from PIL import Image, UnidentifiedImageError
import io

class FileValidator:
    # 允许的图片格式及其对应的 MIME 类型
    ALLOWED_IMAGE_TYPES = {
        'jpeg': 'image/jpeg',
        'jpg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp',
        'bmp': 'image/bmp',
        'tiff': 'image/tiff',
        'svg': 'image/svg+xml',
        'ico': 'image/x-icon',
        'heic': 'image/heic'
    }
    
    # 文件大小限制 (5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    # 图片尺寸限制
    MIN_IMAGE_SIZE = (100, 100)
    MAX_IMAGE_SIZE = (2000, 2000)
    RESIZE_THRESHOLD = (1000, 1000)

    @classmethod
    async def validate_image(cls, file: UploadFile) -> Tuple[bytes, str]:
        """
        Validate and process image file
        
        Args:
            file: UploadFile object
        
        Returns:
            Tuple[bytes, str]: Processed file content and image type
        
        Raises:
            HTTPException: With user-friendly error messages
        """
        try:
            # 检查文件是否为空
            if not file.filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No file was uploaded"
                )

            # 检查文件大小
            file_size = 0
            content = bytearray()
            
            chunk = await file.read(8192)
            while chunk:
                content.extend(chunk)
                file_size += len(chunk)
                if file_size > cls.MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds the limit of "
                            f"{cls.MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
                        )
                    )
                chunk = await file.read(8192)
            
            content_bytes = bytes(content)
            
            # 检查文件类型
            try:
                with Image.open(io.BytesIO(content_bytes)) as img:
                    image_type = img.format.lower()
                    if image_type not in cls.ALLOWED_IMAGE_TYPES:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Unsupported image format: {image_type}. "
                                f"Supported formats are: {', '.join(cls.ALLOWED_IMAGE_TYPES.keys())}"
                            )
                        )
                    
                    # 检查图片尺寸
                    width, height = img.size
                    
                    if width < cls.MIN_IMAGE_SIZE[0] or height < cls.MIN_IMAGE_SIZE[1]:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Image is too small ({width}x{height}). "
                                f"Minimum size is {cls.MIN_IMAGE_SIZE[0]}x{cls.MIN_IMAGE_SIZE[1]} pixels"
                            )
                        )
                    
                    if width > cls.MAX_IMAGE_SIZE[0] or height > cls.MAX_IMAGE_SIZE[1]:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Image is too large ({width}x{height}). "
                                f"Maximum size is {cls.MAX_IMAGE_SIZE[0]}x{cls.MAX_IMAGE_SIZE[1]} pixels"
                            )
                        )
                    
                    # 处理大图片
                    if width > cls.RESIZE_THRESHOLD[0] or height > cls.RESIZE_THRESHOLD[1]:
                        img.thumbnail(cls.RESIZE_THRESHOLD, Image.Resampling.LANCZOS)
                        output = io.BytesIO()
                        
                        # 保持原始格式，除非是不常见的格式
                        save_format = image_type if image_type in ['jpeg', 'png', 'webp'] else 'jpeg'
                        
                        # 根据格式设置保存参数
                        save_params = {}
                        if save_format == 'jpeg':
                            save_params['quality'] = 85
                            save_params['optimize'] = True
                        elif save_format == 'png':
                            save_params['optimize'] = True
                        elif save_format == 'webp':
                            save_params['quality'] = 85
                            save_params['method'] = 6
                        
                        img.save(output, format=save_format, **save_params)
                        content_bytes = output.getvalue()
                        image_type = save_format
            
            except UnidentifiedImageError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The uploaded file is not a valid image"
                )
            
            return content_bytes, image_type

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing image: {str(e)}"
            ) 