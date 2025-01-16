from fastapi import UploadFile, HTTPException
import filetype

async def validate_image(file: UploadFile) -> UploadFile:
    """Validate if file is a valid image"""
    content = await file.read(1024)
    file.file.seek(0)
    
    kind = filetype.guess(content)
    if not kind or not kind.mime.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        )
    
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large"
        )
    
    return file
