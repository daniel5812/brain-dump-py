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
print("[onboarding] Loading Onboarding Router - Version: DEPLOY_V3_CLEAN")

# -----------------------------------------------------------------------------
# SCHEMAS (Local or imported, keeping it simple as requested)
# -----------------------------------------------------------------------------

class VerifyUserRequest(BaseModel):
    user_id: str

class VerifyUserResponse(BaseModel):
    status: str
    phone: str = None
    registration_url: str = None

class RegisterCompleteRequest(BaseModel):
    user_id: str
    phone: str
    email: str
    calendar_enabled: bool

class RegisterCompleteResponse(BaseModel):
    status: str

@router.get("/verify-user", response_model=VerifyUserResponse)
@router.post("/verify-user", response_model=VerifyUserResponse)
async def verify_user_endpoint(request: Request = None, data: VerifyUserRequest = None):
    """
    Checks if a device is registered and returns the associated phone number.
    Supports both GET (with query param) and POST (with body).
    """
    # Try to get device_id from POST body or GET query param
    device_id = None
    if data:
        device_id = data.user_id
    elif request:
        device_id = request.query_params.get("user_id")

    if not device_id:
        return VerifyUserResponse(status="MISSING_ID")

    from crud.user_details import get_user_by_device
    user = get_user_by_device(device_id)
    
    if user and user.get("calendar_enabled"):
        return VerifyUserResponse(
            status="OK",
            phone=user["user_id"] # The phone number is our primary user_id
        )
    
    # Generate a friendly registration URL for the shortcut to use directly
    reg_url = f"https://brain-dump-py.onrender.com/register?user_id={device_id}"
    return VerifyUserResponse(status="NEEDS_REGISTRATION", registration_url=reg_url)


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    """
    GET /register
    Serves the registration HTML page.
    """
    # Robust path resolution for Render/Local
    # We look for static/register.html relative to the root or this file
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "register.html"),
        os.path.join(os.getcwd(), "static", "register.html"),
        os.path.join(os.getcwd(), "backend", "static", "register.html"),
    ]
    
    static_file = None
    for path in possible_paths:
        if os.path.exists(path):
            static_file = path
            break
            
    if static_file:
        print(f"[onboarding] Serving register page from: {static_file}")
        with open(static_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        print(f"[onboarding] ERROR: Register page NOT FOUND. Searched in: {possible_paths}")
        return HTMLResponse(content="<h1>Error: Register page not found</h1>", status_code=404)


@router.post("/register", response_model=RegisterCompleteResponse)
async def complete_registration(request: RegisterCompleteRequest):
    """
    POST /register
    Saves the mapping between technical user_id and manual phone/email.
    """
    # 1. Verify real access to the calendar
    has_access = calendar_client.verify_access(request.email)
    
    if not has_access:
        print(f"[onboarding] Verification FAILED for {request.email}")
        raise HTTPException(
            status_code=403, 
            detail=f"We couldn't access the calendar for {request.email}. "
                   f"Please make sure you shared it correctly with the agent email."
        )

    # 2. Save user data (mapping technical ID to phone/email)
    user_data = {
        "user_id": request.user_id, # Technical ID from Shortcut
        "phone": request.phone,     # Manual Phone from HTML
        "email": request.email,     # Manual Email from HTML
        "calendar_enabled": request.calendar_enabled
    }
    
    register_user(user_data)
    
    print(f"[onboarding] User {request.user_id} registered with phone {request.phone}")
    return RegisterCompleteResponse(status="OK")
