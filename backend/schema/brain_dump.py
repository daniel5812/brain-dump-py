"""
schema/brain_dump.py - Pydantic Models

This file defines the shape of data for the Brain Dump API.

Why use Pydantic models?
1. Automatic validation - invalid data is rejected before your code runs
2. Type hints - your IDE knows what fields exist
3. Documentation - FastAPI generates OpenAPI docs from these
4. Serialization - easy conversion to/from JSON

This file contains ONLY data shapes:
- NO business logic
- NO database queries
- NO external API calls
"""

from pydantic import BaseModel
from typing import Optional


class BrainDumpRequest(BaseModel):
    """
    The request body sent by the iPhone Shortcut.
    
    For Step 1, we only need:
    - text: The transcribed voice message
    - user_id: Who is sending this (for verification)
    
    Later we may add:
    - timestamp
    - audio_url
    - device_info
    """
    text: str  # The transcribed voice message
    user_id: str  # Identifier for user verification


class BrainDumpResponse(BaseModel):
    """
    The response sent back to the iPhone Shortcut.
    
    
    For Step 4/5, we return:
    - success: Did the request complete?
    - message: Human-readable feedback
    - action_taken: What did the server do?
    - status: SUCCESS, NEEDS_CLARIFICATION, FAILED_VALIDATION, or NEEDS_REGISTRATION
    - registration_url: If status is NEEDS_REGISTRATION, this URL can be used for registration.
    """
    success: bool
    message: str
    action_taken: Optional[str] = None
    status: Optional[str] = "SUCCESS"  # Default to SUCCESS for backward compatibility
    registration_url: Optional[str] = None
    actions: Optional[list] = None  # Structured action results (type, payload, etc.)
