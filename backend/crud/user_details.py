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

def verify_user(user_id: str) -> bool:
    """
    Verify that the user is registered in Supabase.
    """
    if not supabase:
        print("[user_details] ERROR: Supabase not connected")
        return False

    try:
        response = supabase.table("users").select("calendar_enabled").eq("user_id", user_id).execute()
        if response.data and len(response.data) > 0:
            is_calendar_ready = response.data[0].get("calendar_enabled", False)
            status = "READY" if is_calendar_ready else "NOT_READY"
            print(f"[user_details] Supabase Verify '{user_id}': {status}")
            return is_calendar_ready
        
        print(f"[user_details] Supabase Verify '{user_id}': NOT_FOUND")
        return False
    except Exception as e:
        print(f"[user_details] Supabase Error during verify: {e}")
        return False


def register_user(user_data: dict) -> dict:
    """
    Register or update a user in Supabase.
    """
    if not supabase:
        raise Exception("Supabase client not initialized")

    user_id = user_data["user_id"]
    is_calendar = user_data.get('calendar_enabled', False)
    
    # Prepare record
    record = {
        "user_id": user_id,
        "name": user_data.get("name", user_id),
        "email": user_data.get("email"),
        "calendar_enabled": is_calendar
    }

    try:
        print(f"[user_details] Upserting user to Supabase: {user_id}")
        # Perform upsert (insert or update on conflict)
        response = supabase.table("users").upsert(record).execute()
        return response.data[0] if response.data else record
    except Exception as e:
        print(f"[user_details] Supabase Error during register: {e}")
        return record


def get_user(user_id: str) -> Optional[dict]:
    """Retrieve user details from Supabase."""
    if not supabase: return None
    try:
        response = supabase.table("users").select("*").eq("user_id", user_id).execute()
        return response.data[0] if response.data else None
    except:
        return None
