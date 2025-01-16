from fastapi import APIRouter
from . import auth, pets, records, reports

router = APIRouter()

# Tags metadata
tags_metadata = [
    {
        "name": "auth",
        "description": "Authentication and user management operations",
    },
    {
        "name": "pets",
        "description": "Pet profile management operations",
    },
    {
        "name": "records",
        "description": "Health record management including weight, vaccines, and medical visits",
    },
    {
        "name": "reports",
        "description": "Generate and manage health reports with customizable templates",
    },
]

__all__ = ["auth", "pets", "records", "reports", "tags_metadata"]
