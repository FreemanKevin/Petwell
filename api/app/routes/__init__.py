from fastapi import APIRouter

router = APIRouter()

# Tags metadata
tags_metadata = [
    {
        "name": "auth",
        "description": "Authentication and user management operations",
    },
    {
        "name": "pets",
        "description": "Pet management operations",
    },
    {
        "name": "records",
        "description": "Pet health records management",
    },
]
