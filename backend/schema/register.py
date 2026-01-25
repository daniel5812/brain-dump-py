"""
schema/register.py - User Registration Models

This file defines the data shape for the /register endpoint.
"""

from pydantic import BaseModel
from typing import Optional


class UserRegistrationRequest(BaseModel):
    """
    Request body for user registration.
    
    The iPhone Shortcut collects this info from the user
    and sends it to /register.
    """
    user_id: str          # The unique ID from the shortcut (e.g., "daniel")
    name: str             # User's display name
    email: Optional[str] = None  # Optional contact info
    phone: Optional[str] = None       # Optional contact info
    preferred_channel: Optional[str] = "whatsapp"  # whatsapp/email/sms


class UserRegistrationResponse(BaseModel):
    """
    Response after successful registration.
    """
    success: bool
    message: str
    user_id: str

class VerifyUserRequest(BaseModel):
    user_id: str

class VerifyUserResponse(BaseModel):
    status: str # "OK" or "NEEDS_REGISTRATION"

class RegisterCompleteRequest(BaseModel):
    user_id: str
    email: str
    calendar_enabled: bool
