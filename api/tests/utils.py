from typing import Dict
from app.core.security import create_access_token

def get_auth_headers(user_id: int) -> Dict[str, str]:
    """Generate authentication headers"""
    access_token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {access_token}"}