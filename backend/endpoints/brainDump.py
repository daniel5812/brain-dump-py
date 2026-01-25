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

from fastapi import APIRouter, HTTPException

# Import our Pydantic models
from schema.brain_dump import BrainDumpRequest, BrainDumpResponse

# Import business logic from their proper homes (Step 2: Clean Separation)
from crud.user_details import verify_user
from tools.business_logic.brain_dump_flow import brain_dump_flow

# Create router for brain dump endpoints
router = APIRouter()


# =============================================================================
# ENDPOINT
# =============================================================================

@router.post("/brain-dump", response_model=BrainDumpResponse)
async def brain_dump(request: BrainDumpRequest):
    """
    Main Brain Dump endpoint.
    
    Receives transcribed voice from iPhone Shortcut,
    processes it through the brain dump flow,
    and returns feedback.
    
    The flow:
    1. Input is validated automatically by Pydantic
    2. User is verified (MUST happen before any processing)
    3. brain_dump_flow handles all the logic
    4. Response is returned
    
    Args:
        request: BrainDumpRequest with text and user_id
        
    Returns:
        BrainDumpResponse with success status and feedback
        
    Raises:
        HTTPException 401: If user is not verified
    """
    # Step 1: Resolve Identity (TECHNICAL ID -> PHONE NUMBER)
    from crud.user_details import get_user_by_device
    
    user_record = get_user_by_device(request.user_id)
    
    if not user_record or not user_record.get("calendar_enabled", False):
        print(f"[endpoint] Device unrecognized or not ready: {request.user_id} -> Asking for registration")
        return BrainDumpResponse(
            success=False,
            message="I need to know who you are to help you. Please provide your details.",
            status="NEEDS_REGISTRATION",
            action_taken=None
        )
    
    # The real User ID for the rest of the flow is the Phone Number
    real_user_id = user_record["user_id"]

    # Step 2: Provide time context for the agent (relative dates like 'tomorrow')
    import os
    from datetime import datetime
    os.environ["CURRENT_TIME_CONTEXT"] = datetime.now().isoformat()

    # Step 3: Call the brain dump flow with the REAL (Phone) user_id
    result = brain_dump_flow(
        text=request.text,
        user_id=real_user_id
    )
    
    # Step 3: Return the response
    # Just passing through what the flow returned
    return BrainDumpResponse(
        success=result["success"],
        message=result["message"],
        action_taken=result.get("action_taken"),
        status=result.get("status", "SUCCESS")
    )
