"""
curd/user_details.py - User Verification & Management

RESPONSIBILITY:
- Verify if a user is registered
- Register new users
- Manage user data (in-memory for Step 5)

WHY THIS FILE EXISTS:
- Separation of concerns: endpoints shouldn't know HOW users are stored
- Single source of truth for user identity

CURRENT STATE (Step 5):
- In-memory dictionary `users_db` replacing the stub
- Registration logic added
- verify_user now checks existence

FUTURE ENHANCEMENTS:
- Database lookup (Supabase)
- Token management
"""

from typing import Optional, Dict
from tools.database.supabase_client import supabase

def verify_user(device_id: str) -> bool:
    """
    Verify that the DEVICE is registered to a user with calendar enabled.
    """
    if not supabase: return False

    try:
        response = supabase.table("users").select("calendar_enabled").eq("device_id", device_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0].get("calendar_enabled", False)
        return False
    except:
        return False


def register_user(user_data: dict) -> dict:
    """
    Register or update a user record.
    user_id = Phone Number
    device_id = Technical ID from Shortcut
    """
    if not supabase:
        raise Exception("Supabase client not initialized")

    # Map the incoming data to our schema: user_id IS the phone
    record = {
        "user_id": user_data["phone"], 
        "device_id": user_data["user_id"], # The technical ID sent from Shortcut
        "email": user_data.get("email"),
        "calendar_enabled": user_data.get("calendar_enabled", False)
    }

    try:
        print(f"[user_details] Upserting Phone Identity: {record['user_id']} for Device: {record['device_id']}")
        response = supabase.table("users").upsert(record).execute()
        return response.data[0] if response.data else record
    except Exception as e:
        print(f"[user_details] Supabase Error: {e}")
        return record


def get_user_by_device(device_id: str) -> Optional[dict]:
    """Resolve the technical Device ID to a full User (Phone) record."""
    if not supabase: return None
    try:
        response = supabase.table("users").select("*").eq("device_id", device_id).execute()
        return response.data[0] if response.data else None
    except:
        return None

def get_user(user_id: str) -> Optional[dict]:
    """Retrieve user details by Phone Number."""
    if not supabase: return None
    try:
        response = supabase.table("users").select("*").eq("user_id", user_id).execute()
        return response.data[0] if response.data else None
    except:
        return None
