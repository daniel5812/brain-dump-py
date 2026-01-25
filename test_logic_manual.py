
import sys
import os
import asyncio

# Setup path to import backend modules
sys.path.append(os.path.join(os.getcwd(), "backend"))

from crud.user_details import verify_user, register_user, users_db

def test_flow():
    print("--- Testing Registration Logic ---")
    user_id = "test_user_123"
    
    # 1. Verify unknown user
    print(f"\n1. Checking verification for unknown user '{user_id}'...")
    is_valid = verify_user(user_id)
    if not is_valid:
        print("✅ Correct: User is not verified yet.")
    else:
        print("❌ Error: Unknown user verified as valid.")

    # 2. Register user WITHOUT calendar
    print(f"\n2. Registering user '{user_id}' without calendar...")
    register_user({"user_id": user_id, "name": "Test", "calendar_enabled": False})
    
    is_valid = verify_user(user_id)
    if not is_valid:
        print("✅ Correct: User exists but calendar not enabled -> not verified.")
    else:
        print("❌ Error: User without calendar verified as valid.")

    # 3. Complete registration (Enable Calendar)
    print(f"\n3. Enabling calendar for '{user_id}'...")
    # Simulate register/complete logic
    register_user({"user_id": user_id, "name": "Test", "calendar_enabled": True})
    
    is_valid = verify_user(user_id)
    if is_valid:
        print("✅ Correct: User with calendar enabled is verified.")
    else:
        print("❌ Error: User with calendar enabled FAILED verification.")
        
    print("\nTest Complete.")

if __name__ == "__main__":
    test_flow()
