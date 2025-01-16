from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.core.storage import upload_file, delete_file
from app.db.session import get_db
from app.models.user import User
from app.models.pet import Pet
from app.schemas.pet import PetCreate, PetUpdate, PetResponse
from app.routes.deps import validate_image

router = APIRouter(
    prefix="/pets",
    tags=["pets"],
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Pet not found"}
    }
)

@router.get("/", response_model=List[PetResponse])
async def list_pets(
    skip: int = Query(0, description="Skip N items"),
    limit: int = Query(100, description="Limit response size"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all pets belonging to current user.
    
    Parameters:
    * **skip**: Number of records to skip (pagination)
    * **limit**: Maximum number of records to return
    
    Returns list of pets with their basic information.
    """
    pets = db.query(Pet).filter(
        Pet.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    return pets

@router.post("/", response_model=PetResponse)
async def create_pet(
    pet_in: PetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new pet profile.
    
    Parameters:
    * **name**: Pet's name
    * **species**: Type of pet (e.g., dog, cat)
    * **gender**: Pet's gender
    * **breed**: Pet's breed (optional)
    * **birth_date**: Pet's birth date (optional)
    
    Returns created pet profile.
    """
    pet = Pet(**pet_in.model_dump(), owner_id=current_user.id)
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet

@router.get("/{pet_id}", response_model=PetResponse)
async def get_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific pet.
    
    Parameters:
    * **pet_id**: ID of the pet to retrieve
    
    Returns detailed pet information including health records.
    
    Raises:
    * **404**: Pet not found
    * **401**: Not authorized to access this pet
    """
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet

@router.put("/{pet_id}", response_model=PetResponse)
async def update_pet(
    pet_id: int,
    pet_in: PetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update pet information.
    
    Parameters:
    * **pet_id**: ID of the pet to update
    * **name**: New name (optional)
    * **status**: New status (optional)
    * **breed**: New breed (optional)
    * **avatar_url**: New avatar URL (optional)
    
    Returns updated pet information.
    
    Raises:
    * **404**: Pet not found
    * **401**: Not authorized to modify this pet
    """
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    # Update fields
    for field, value in pet_in.dict(exclude_unset=True).items():
        setattr(pet, field, value)
    
    db.commit()
    db.refresh(pet)
    return pet

@router.delete("/{pet_id}")
async def delete_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a pet profile.
    
    Parameters:
    * **pet_id**: ID of the pet to delete
    
    Returns:
    * **status**: Success message
    
    Raises:
    * **404**: Pet not found
    * **401**: Not authorized to delete this pet
    """
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    db.delete(pet)
    db.commit()
    return {"status": "success"}

@router.post("/{pet_id}/avatar")
async def upload_avatar(
    pet_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a profile picture for a pet.
    
    Parameters:
    * **pet_id**: ID of the pet
    * **file**: Image file (JPG, PNG, or GIF)
    
    Returns:
    * **avatar_url**: URL of the uploaded image
    
    Raises:
    * **400**: Invalid image file
    * **404**: Pet not found
    * **401**: Not authorized to modify this pet
    """
    # Verify pet ownership
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.owner_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    # Validate image file
    file = await validate_image(file)
    
    try:
        # Upload file to Minio
        avatar_url = await upload_file(
            file=file,
            folder="avatars",
            filename=f"pet_{pet_id}_{int(datetime.now().timestamp())}"
        )
        
        # Delete old avatar if exists
        if pet.avatar_url:
            old_path = pet.avatar_url.split("/")[-2:]  # Get folder/filename
            await delete_file("/".join(old_path))
        
        # Update pet avatar URL
        pet.avatar_url = avatar_url
        db.commit()
        
        return {"avatar_url": avatar_url}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )
