"""
tools/actions/action_executor.py - Action Execution Layer (STUB)

═══════════════════════════════════════════════════════════════════════════════
RESPONSIBILITY
═══════════════════════════════════════════════════════════════════════════════

This file is the ACTION EXECUTION LAYER.

Input:  List of actions (from decision engine)
Output: List of execution results

CURRENT STATE (Step 4): STUB IMPLEMENTATION
- Does NOT make real API calls
- Does NOT access database
- Does NOT send emails/messages
- Just LOGS what WOULD happen

FUTURE STATE (Step 5+):
- Real Todoist integration
- Real Calendar integration
- Real database storage
- Real notifications

═══════════════════════════════════════════════════════════════════════════════
ACTION TYPES (Step 4 - All stubs)
═══════════════════════════════════════════════════════════════════════════════

CREATE_TASK       - Would add task to Todoist
CREATE_EVENT      - Would add event to Google Calendar
CREATE_REMINDER   - Would set reminder
SAVE_NOTE         - Would save note to database
"""


def execute(actions: list[dict], user_id: str) -> list[dict]:
    """
    Execute a list of actions (STUB - no real execution yet).
    
    This is the ACTION EXECUTOR's main function.
    For Step 4, it just logs what WOULD happen and returns success.
    
    Args:
        actions (list[dict]): List of actions from decision engine
            Each action has:
            {
                "type": str,      # Action type (CREATE_TASK, CREATE_EVENT, etc.)
                "payload": dict   # Action-specific data
            }
        user_id (str): User identifier
        
    Returns:
        list[dict]: Execution results
            Each result has:
            {
                "ok": bool,           # Was execution successful?
                "type": str,          # Action type that was executed
                "details": str,       # What happened (stub message)
                "payload": dict       # Original payload (for debugging)
            }
            
    Example:
        >>> actions = [{"type": "CREATE_TASK", "payload": {"title": "Buy milk"}}]
        >>> execute(actions, "daniel")
        [
            {
                "ok": True,
                "type": "CREATE_TASK",
                "details": "STUB: Would add task 'Buy milk' to Todoist",
                "payload": {"title": "Buy milk"}
            }
        ]
    """
    if not actions:
        print("[action_executor] No actions to execute")
        return []
    
    print(f"[action_executor] Executing {len(actions)} action(s) for user: {user_id}")
    
    results = []
    
    for action in actions:
        action_type = action.get("type", "UNKNOWN")
        payload = action.get("payload", {})
        
        print(f"[action_executor] Processing action: {action_type}")
        
        # Route to specific action handler (all stubs for now)
        if action_type == "CREATE_TASK":
            result = _execute_create_task(payload, user_id)
        elif action_type == "CREATE_EVENT":
            result = _execute_create_event(payload, user_id)
        elif action_type == "CREATE_REMINDER":
            result = _execute_create_reminder(payload, user_id)
        elif action_type == "SAVE_NOTE":
            result = _execute_save_note(payload, user_id)
        else:
            result = {
                "ok": False,
                "type": action_type,
                "details": f"STUB: Unknown action type '{action_type}'",
                "payload": payload
            }
        
        results.append(result)
        print(f"[action_executor] Result: {result['details']}")
    
    return results


# =============================================================================
# ACTION-SPECIFIC STUB EXECUTORS
# =============================================================================

def _execute_create_task(payload: dict, user_id: str) -> dict:
    """
    STUB: Would create a task in Todoist.
    
    Future (Step 5+):
    - Call Todoist API
    - Create task with title, due date, priority
    - Return task ID
    """
    title = payload.get("title", "Untitled task")
    
    # STUB: Just log what would happen
    stub_message = f"STUB: Would add task '{title}' to Todoist for user {user_id}"
    
    return {
        "ok": True,
        "type": "CREATE_TASK",
        "details": stub_message,
        "payload": payload
    }


def _execute_create_event(payload: dict, user_id: str) -> dict:
    """
    Creates a real event in Google Calendar.
    Requires the user's email to be registered in Supabase.
    """
    from tools.google_calendar.calendar_client import calendar_client
    from crud.user_details import get_user
    
    # 1. Get user email from Supabase
    user = get_user(user_id)
    if not user or not user.get("email"):
        return {
            "ok": False,
            "type": "CREATE_EVENT",
            "details": f"ERROR: No registered email found for user {user_id}",
            "payload": payload
        }
    
    calendar_id = user["email"]
    title = payload.get("title") or payload.get("title_raw", "Brain Dump Event")
    start_iso = payload.get("start_iso")
    end_iso = payload.get("end_iso")
    description = f"Created via Brain Dump for {user_id}"

    if not start_iso:
        return {
            "ok": False,
            "type": "CREATE_EVENT",
            "details": "ERROR: No start time provided for the event",
            "payload": payload
        }

    # 2. Call the real calendar client
    result = calendar_client.create_event(
        calendar_id=calendar_id,
        title=title,
        start_iso=start_iso,
        end_iso=end_iso,
        description=description
    )

    if result["ok"]:
        return {
            "ok": True,
            "type": "CREATE_EVENT",
            "details": f"Event '{title}' created successfully! Check your calendar.",
            "payload": {"event_link": result.get("link")}
        }
    else:
        return {
            "ok": False,
            "type": "CREATE_EVENT",
            "details": f"Failed to create event: {result.get('error')}",
            "payload": payload
        }


def _execute_create_reminder(payload: dict, user_id: str) -> dict:
    """
    STUB: Would create a reminder.
    
    Future (Step 5+):
    - Store reminder in database
    - Set up notification trigger
    - Return reminder ID
    """
    title = payload.get("title", "Untitled reminder")
    when_raw = payload.get("when_raw", "unspecified time")
    
    # STUB: Just log what would happen
    stub_message = f"STUB: Would set reminder '{title}' for '{when_raw}' for user {user_id}"
    
    return {
        "ok": True,
        "type": "CREATE_REMINDER",
        "details": stub_message,
        "payload": payload
    }


def _execute_save_note(payload: dict, user_id: str) -> dict:
    """
    STUB: Would save a note to database.
    Notes are currently non-blocking and not saved to Supabase yet.
    """
    content = payload.get("content", "Empty note")
    print(f"[action_executor] STUB: SAVE_NOTE requested for {user_id}: '{content}'")
    
    return {
        "ok": True,
        "type": "SAVE_NOTE",
        "details": f"STUB: SAVE_NOTE logged for {user_id}",
        "payload": payload
    }
