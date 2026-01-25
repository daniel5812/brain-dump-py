"""
endpoints/user_onboarding.py - User Verification & Registration Routes

RESPONSIBILITIES:
- Handle /verify-user
- Handle /register (Serve HTML)
- Handle /register/complete

AUTHORITY:
- Uses crud.user_details for logic
- Uses static files for HTML
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os

from crud.user_details import verify_user, register_user
from tools.google_calendar.calendar_client import calendar_client

router = APIRouter()

# -----------------------------------------------------------------------------
# SCHEMAS (Local or imported, keeping it simple as requested)
# -----------------------------------------------------------------------------

class VerifyUserRequest(BaseModel):
    user_id: str

class VerifyUserResponse(BaseModel):
    status: str

class RegisterCompleteRequest(BaseModel):
    user_id: str
    email: str
    calendar_enabled: bool

class RegisterCompleteResponse(BaseModel):
    status: str

# -----------------------------------------------------------------------------
# ROUTES
# -----------------------------------------------------------------------------

@router.post("/verify-user", response_model=VerifyUserResponse)
async def verify_user_endpoint(request: VerifyUserRequest):
    """
    POST /verify-user
    Checks if a user is registered and ready.
    """
    is_valid = verify_user(request.user_id)
    status = "OK" if is_valid else "NEEDS_REGISTRATION"
    return VerifyUserResponse(status=status)


@router.get("/register", response_class=HTMLResponse)
async def get_register_page():
    """
    GET /register
    Serves the registration HTML page.
    """
    # Assuming execution from backend/ root or consistent path
    # We'll use absolute path logic to find static/register.html
    
    current_dir = os.path.dirname(os.path.abspath(__file__)) # endpoints/
    backend_dir = os.path.dirname(current_dir) # backend/
    static_file = os.path.join(backend_dir, "static", "register.html")
    
    if os.path.exists(static_file):
        with open(static_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="<h1>Error: Register page not found</h1>", status_code=404)


@router.post("/register/complete", response_model=RegisterCompleteResponse)
async def complete_registration(request: RegisterCompleteRequest):
    """
    POST /register/complete
    Finalizes registration (saves flag after REAL verification).
    """
    # 1. Verify real access to the calendar
    # We use the provided email as the calendar ID
    has_access = calendar_client.verify_access(request.email)
    
    if not has_access:
        print(f"[onboarding] Verification FAILED for {request.email}")
        raise HTTPException(
            status_code=403, 
            detail=f"We couldn't access the calendar for {request.email}. "
                   f"Please make sure you shared it correctly with the agent email."
        )

    # 2. If verified, save user data
    user_data = {
        "user_id": request.user_id,
        "email": request.email,
        "calendar_enabled": request.calendar_enabled
    }
    
    register_user(user_data)
    
    print(f"[onboarding] Registration completed and VERIFIED for {request.user_id}")
    return RegisterCompleteResponse(status="OK")
