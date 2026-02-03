"""
endpoints/brainDump.py - Main Brain Dump Endpoint

This file handles the /brain-dump POST endpoint.

THE FLOW (even in Step 1):
1. Receive request
2. Validate input (automatic via Pydantic)
3. Verify user (stub for now)
4. Call brain_dump_flow (stub for now)
5. Return response

STRICT RESPONSIBILITIES:
✅ HTTP request handling
✅ Input validation
✅ Calling user verification
✅ Calling the business logic flow
✅ Returning HTTP response

❌ NO intent classification
❌ NO business decisions
❌ NO action execution
❌ NO database knowledge
"""

from fastapi import APIRouter, HTTPException, Request, Body, Query
from typing import Optional

# Import our Pydantic models
from schema.brain_dump import BrainDumpRequest, BrainDumpResponse

# Import business logic
from crud.user_details import verify_user
from tools.business_logic.brain_dump_flow import brain_dump_flow

# Create router for brain dump endpoints
router = APIRouter()


# =============================================================================
# ENDPOINT
@router.post("/brain-dump", response_model=BrainDumpResponse)
@router.get("/brain-dump", response_model=BrainDumpResponse) # Also support GET for easier testing
async def brain_dump(
    request: Request,
    body: Optional[dict] = Body(None),
    text: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None)
):
    """
    Flexible Brain Dump endpoint.
    Handles data from JSON body, Form data, or Query params.
    """
    # 1. TRIPLE FALLBACK LOGIC
    final_text = text
    final_user_id = user_id

    # If body exists (JSON), use it
    if body:
        final_text = body.get("text", final_text)
        final_user_id = body.get("user_id", final_user_id)
        # Handle common naming variations in Shortcuts
        final_user_id = body.get("userId", final_user_id)
        final_user_id = body.get("TechnicalID", final_user_id)

    # If still missing, check Form data
    if not final_text or not final_user_id:
        form_data = await request.form()
        final_text = form_data.get("text", final_text)
        final_user_id = form_data.get("user_id", final_user_id)

    # 2. VALIDATION (Be specific to allow '0' as a value)
    if final_text is None or final_text == "" or final_user_id is None or final_user_id == "":
        print(f"[endpoint] VALIDATION FAILED: text='{final_text}', user_id='{final_user_id}' (Type: {type(final_user_id)})")
        return BrainDumpResponse(
            success=False,
            message="Missing required fields: 'text' or 'user_id'. Please check your Shortcut configuration.",
            status="FAILED_VALIDATION"
        )

    # Ensure user_id is a string for database lookups
    final_user_id = str(final_user_id)
    print(f"[endpoint] Processing request: user='{final_user_id}', text='{final_text[:20]}...' | Method: {request.method}")

    # Step 1: Resolve Identity (TECHNICAL ID -> PHONE NUMBER)
    from crud.user_details import get_user_by_device
    
    # SPECIAL DEBUG: If user_id is "0", it means the Shortcut is passing a null 'phone' from a failed verification.
    if final_user_id == "0":
        print(f"[endpoint] WARNING: Received user_id='0'. Shortcut mapping error.")
        return BrainDumpResponse(
            success=False,
            message="שגיאה בקיצור הדרך: ה-user_id שהתקבל הוא '0'. בקיצור הדרך שלך, בשלב של שליחת ה-Brain Dump, וודא שאתה שולח את המשתנה TechnicalID ולא את תוצאת האימות.",
            status="NEEDS_REGISTRATION",
            registration_url=f"https://brain-dump-py.onrender.com/register?user_id=Daniel_iPhone" # Fallback if they still need it
        )

    user_record = get_user_by_device(final_user_id)
    
    if not user_record or not user_record.get("calendar_enabled", False):
        print(f"[endpoint] Device unrecognized or not ready: {final_user_id} -> Asking for registration")
        reg_url = f"https://brain-dump-py.onrender.com/register?user_id={final_user_id}"
        return BrainDumpResponse(
            success=False,
            message="I need to know who you are to help you. Click below to register.",
            status="NEEDS_REGISTRATION",
            registration_url=reg_url,
            action_taken=None
        )
    
    # The real User ID for the rest of the flow is the Phone Number
    real_user_id = user_record["user_id"]

    # Step 2: Provide time context
    import os
    from datetime import datetime
    os.environ["CURRENT_TIME_CONTEXT"] = datetime.now().isoformat()

    # Step 3: Call the brain dump flow
    result = brain_dump_flow(
        text=final_text,
        user_id=real_user_id
    )
    
    # SPECIAL HANDLING FOR NOTES (Contract Check)
    # The notes contract requires a STRICT format without the 'success' field or others.
    # We must bypass the standard BrainDumpResponse model.
    if result.get("intent") == "note":
        from fastapi.responses import JSONResponse
        return JSONResponse(content=result)
    
    # Standard response for all other flows
    return BrainDumpResponse(
        success=result.get("success", False), # Default to False if missing
        message=result.get("message", ""),
        action_taken=result.get("action_taken"),
        status=result.get("status", "SUCCESS"),
        actions=result.get("debug", {}).get("execution_results")
    )
