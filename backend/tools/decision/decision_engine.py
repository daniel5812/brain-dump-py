"""
tools/decision/decision_engine.py - Decision Layer

═══════════════════════════════════════════════════════════════════════════════
RESPONSIBILITY
═══════════════════════════════════════════════════════════════════════════════

This file is the DECISION LAYER.

Input:  Intent result (from agent) + user context
Output: Decision with status, actions, and feedback

This file does NOT:
- Execute actions (that's action_executor.py)
- Classify intent (that's agent_process.py)
- Orchestrate flow (that's brain_dump_flow.py)
- Make HTTP calls
- Access database directly

═══════════════════════════════════════════════════════════════════════════════
STATUS CODES
═══════════════════════════════════════════════════════════════════════════════

SUCCESS               - Intent is clear, all required info present, actions created
NEEDS_CLARIFICATION   - Intent understood but missing required information
FAILED_VALIDATION     - Intent understood but info provided is invalid/insufficient
SYSTEM_ERROR          - Something went wrong internally

═══════════════════════════════════════════════════════════════════════════════
ACTION TYPES (Step 4 - All stubs)
═══════════════════════════════════════════════════════════════════════════════

CREATE_TASK           - Add task to todo list
CREATE_EVENT          - Add event to calendar
CREATE_REMINDER       - Set reminder
SAVE_NOTE             - Save note/idea
"""


from datetime import datetime


# Status codes
STATUS_SUCCESS = "SUCCESS"
STATUS_NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
STATUS_FAILED_VALIDATION = "FAILED_VALIDATION"
STATUS_SYSTEM_ERROR = "SYSTEM_ERROR"

# Action types
ACTION_CREATE_EVENT = "CREATE_EVENT"
ACTION_CREATE_REMINDER = "CREATE_REMINDER"
ACTION_CREATE_ALARM = "CREATE_ALARM"
ACTION_SAVE_NOTE = "SAVE_NOTE"
ACTION_ADD_SHOPPING = "ADD_SHOPPING"


def decide(intent_result: dict, user_id: str) -> dict:
    """
    Decide what actions to take based on intent classification result.
    
    This is the DECISION LAYER's main function.
    It validates that we have enough information and creates action plans.
    
    Args:
        intent_result (dict): Result from agent_process.process_text()
            {
                "intent": str,
                "confidence": float,
                "entities": dict,
                "original_text": str
            }
        user_id (str): User identifier (for future user-specific rules)
        
    Returns:
        dict: Decision result
            {
                "status": str,              # SUCCESS / NEEDS_CLARIFICATION / FAILED_VALIDATION / SYSTEM_ERROR
                "actions": list[dict],      # Actions to execute (empty if clarification needed)
                "feedback": str,            # User-facing message
                "debug": dict              # Optional debug info
            }
            
    Example:
        >>> intent = {"intent": "task", "confidence": 0.95, "entities": {"raw": "milk"}, "original_text": "Add milk"}
        >>> decide(intent, "daniel")
        {
            "status": "SUCCESS",
            "actions": [{"type": "CREATE_TASK", "payload": {"title": "Add milk", ...}}],
            "feedback": "I'll add this task for you...",
            "debug": {"intent": "task", "confidence": 0.95}
        }
    """
    try:
        intent = intent_result.get("intent", "unknown")
        entities = intent_result.get("entities", {})
        original_text = intent_result.get("original_text", "")
        confidence = intent_result.get("confidence", 0.0)
        
        print(f"[decision_engine] Processing intent: {intent}")
        print(f"[decision_engine] Entities: {entities}")
        
        # Route to specific intent handler
        if intent == "task":
            # Task is treated as a reminder (no time)
            return _decide_reminder(original_text, entities, user_id, confidence)
        elif intent == "event":
            return _decide_event(original_text, entities, user_id, confidence)
        elif intent == "reminder":
            return _decide_reminder(original_text, entities, user_id, confidence)
        elif intent == "alarm":
            return _decide_alarm(original_text, entities, user_id, confidence)
        elif intent == "note":
            return _decide_note(original_text, entities, user_id, confidence)
        elif intent == "shopping":
            return _decide_shopping(original_text, entities, user_id, confidence)
        elif intent == "question":
            return _decide_question(original_text, entities, user_id, confidence)
        else:  # unknown
            return _decide_unknown(original_text, entities, user_id, confidence)
            
    except Exception as e:
        print(f"[decision_engine] ERROR: {e}")
        return {
            "status": STATUS_SYSTEM_ERROR,
            "actions": [],
            "feedback": "Sorry, something went wrong. / סליחה, משהו השתבש בעיבוד הבקשה.",
            "debug": {"error": str(e)}
        }


# =============================================================================
# INTENT-SPECIFIC DECISION FUNCTIONS
# =============================================================================

def _decide_task(text: str, entities: dict, user_id: str, confidence: float) -> dict:
    """
    Decide what to do for task intent.
    
    Rules:
    - If entities contain task info → SUCCESS with CREATE_TASK action
    - If missing task info → FAILED_VALIDATION asking what to add
    """
    # Check if we have something to create a task from
    # Entities might be empty or have "raw" key from OpenAI
    has_task_info = bool(text.strip()) and (
        bool(entities.get("raw")) or 
        bool(entities.get("item")) or
        bool(entities.get("task"))
    )
    
    if has_task_info:
        # SUCCESS - we have enough to create a task
        action = {
            "type": ACTION_CREATE_TASK,
            "payload": {
                "title": entities.get("title") or entities.get("item") or text,
                "entities_raw": entities.get("raw", ""),
                "user_id": user_id,
                **entities # Pass all extracted entities
            }
        }
        
        return {
            "status": STATUS_SUCCESS,
            "actions": [action],
            "feedback": f"I'll add this task for you: '{text}' / הוספתי את המשימה: '{text}'",
            "debug": {"intent": "task", "confidence": confidence}
        }
    else:
        # FAILED_VALIDATION - missing task info
        return {
            "status": STATUS_FAILED_VALIDATION,
            "actions": [],
            "feedback": "I understand you want to add a task, but what should the task be? / הבנתי שרצית להוסיף משימה, אבל מה המשימה?",
            "debug": {"intent": "task", "confidence": confidence, "reason": "missing_task_info"}
        }


def _decide_event(text: str, entities: dict, user_id: str, confidence: float) -> dict:
    """
    Decide what to do for event intent.
    
    Rules:
    - If entities contain time/date → SUCCESS with CREATE_EVENT action
    - If missing time/date → NEEDS_CLARIFICATION asking when
    """
    # Check if we have time/date information
    entity_raw = entities.get("raw", "").lower()
    has_time_info = (
        "time=" in entity_raw or 
        "date=" in entity_raw or
        entities.get("time") or 
        entities.get("date") or
        entities.get("when") or
        entities.get("start_iso") # Add support for our new ISO format
    )
    
    if has_time_info:
        # SUCCESS - we have enough to create an event
        action = {
            "type": ACTION_CREATE_EVENT,
            "payload": {
                "title": entities.get("title") or text,
                "when_raw": entity_raw or text,
                "user_id": user_id,
                **entities # This will include start_iso, end_iso, etc.
            }
        }
        
        return {
            "status": STATUS_SUCCESS,
            "actions": [action],
            "feedback": f"I'll schedule this event for you: '{text}' / קבעתי לך את האירוע: '{text}'",
            "debug": {"intent": "event", "confidence": confidence}
        }
    else:
        # NEEDS_CLARIFICATION - missing time info
        return {
            "status": STATUS_NEEDS_CLARIFICATION,
            "actions": [],
            "feedback": f"I understand you want to schedule '{text}', but when should it be? / הבנתי שאתה רוצה לקבוע את '{text}', אבל מתי?",
            "debug": {"intent": "event", "confidence": confidence, "reason": "missing_time"}
        }


def _decide_reminder(text: str, entities: dict, user_id: str, confidence: float) -> dict:
    """
    Decide what to do for reminder intent.
    
    Rules:
    - If entities contain time → SUCCESS with reminder details
    - If missing time → NEEDS_CLARIFICATION asking when
    
    CONTRACT for Shortcut:
    - reminder_title: The reminder text/title
    - reminder_iso: Full ISO 8601 datetime string (e.g., "2026-02-06T17:00:00")
      Apple Shortcuts can parse this directly into a Date object for the alert field.
    - clarification_for: What info is missing (only when NEEDS_CLARIFICATION)
    """
    # Extract the reminder title (what to remind about)
    reminder_title = entities.get("title") or entities.get("reminder") or entities.get("task") or text
    
    # Check if we have time information
    entity_raw = entities.get("raw", "").lower()
    start_iso = entities.get("start_iso")  # ISO format from agent
    time_only = entities.get("time")  # Just time like "17:00"
    
    has_time_info = (
        start_iso or
        time_only or
        "time=" in entity_raw or 
        "in " in text.lower() or  # "remind me in 1 hour"
        "at " in text.lower() or  # "remind me at 5pm"
        "בשעה" in text or  # Hebrew "at hour"
        "ב-" in text  # Hebrew time prefix
    )
    
    if has_time_info:
        # SUCCESS - we have time info
        # Build a full ISO 8601 datetime string for the Shortcut
        reminder_iso = None
        
        if start_iso:
            # Validate and normalize ISO format: "2026-02-06T17:00:00"
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(start_iso)
                reminder_iso = dt.strftime("%Y-%m-%dT%H:%M:%S")
            except:
                pass
        
        if not reminder_iso and time_only:
            # Build ISO from time_only + today's date
            try:
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")
                reminder_iso = f"{today}T{time_only}:00"
            except:
                pass
        
        action = {
            "type": ACTION_CREATE_REMINDER,
            "payload": {
                "title": reminder_title,
                "when_raw": entity_raw or text,
                "user_id": user_id,
                **entities
            }
        }
        
        # Format feedback message (human-readable)
        feedback_msg = f"תזכורת נקבעה: '{reminder_title}'"
        if reminder_iso:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(reminder_iso)
                feedback_msg += f" ב-{dt.strftime('%H:%M')} ({dt.strftime('%Y-%m-%d')})"
            except:
                feedback_msg += f" ({reminder_iso})"
        
        return {
            "status": STATUS_SUCCESS,
            "actions": [action],
            "feedback": feedback_msg,
            "reminder_title": reminder_title,
            "reminder_iso": reminder_iso,  # Full ISO 8601: "2026-02-10T16:00:00"
            "debug": {"intent": "reminder", "confidence": confidence}
        }
    else:
        # NEEDS_CLARIFICATION - missing time
        return {
            "status": STATUS_NEEDS_CLARIFICATION,
            "actions": [],
            "feedback": f"מתי להזכיר לך על '{reminder_title}'?",
            "reminder_title": reminder_title,
            "reminder_time": None,
            "reminder_date": None,
            "clarification_for": "time",
            "debug": {"intent": "reminder", "confidence": confidence, "reason": "missing_time"}
        }


def _decide_alarm(text: str, entities: dict, user_id: str, confidence: float) -> dict:
    """
    Decide what to do for alarm intent.
    
    Rules:
    - If time is present → SUCCESS with alarm details
    - If missing time → NEEDS_CLARIFICATION asking when
    
    CONTRACT for Shortcut:
    - alarm_iso: Full ISO 8601 datetime string for the alarm
    - alarm_label: Optional label/reason for the alarm (empty string if none)
    """
    # Extract the alarm label (reason/description)
    alarm_label = entities.get("label") or entities.get("title") or ""
    
    # Check if we have time information
    start_iso = entities.get("start_iso")
    
    if start_iso:
        # SUCCESS - we have time info
        alarm_iso = None
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(start_iso)
            alarm_iso = dt.strftime("%Y-%m-%dT%H:%M:%S")
        except:
            pass
        
        if not alarm_iso:
            return {
                "status": STATUS_NEEDS_CLARIFICATION,
                "actions": [],
                "feedback": "לא הצלחתי לפענח את השעה. מתי לקבוע את השעון מעורר?",
                "alarm_label": alarm_label,
                "alarm_iso": None,
                "clarification_for": "time",
                "debug": {"intent": "alarm", "confidence": confidence, "reason": "invalid_time"}
            }
        
        # Format feedback
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(alarm_iso)
            time_str = dt.strftime("%H:%M")
            date_str = dt.strftime("%Y-%m-%d")
            feedback_msg = f"שעון מעורר נקבע ל-{time_str}"
            # Only mention date if it's not today
            today = datetime.now().strftime("%Y-%m-%d")
            if date_str != today:
                feedback_msg += f" ({date_str})"
            if alarm_label:
                feedback_msg += f" — {alarm_label}"
        except:
            feedback_msg = f"שעון מעורר נקבע ({alarm_iso})"
        
        action = {
            "type": ACTION_CREATE_ALARM,
            "payload": {
                "alarm_iso": alarm_iso,
                "label": alarm_label,
                "user_id": user_id
            }
        }
        
        return {
            "status": STATUS_SUCCESS,
            "actions": [action],
            "feedback": feedback_msg,
            "alarm_iso": alarm_iso,
            "alarm_label": alarm_label,
            "debug": {"intent": "alarm", "confidence": confidence}
        }
    else:
        # NEEDS_CLARIFICATION - missing time
        return {
            "status": STATUS_NEEDS_CLARIFICATION,
            "actions": [],
            "feedback": "מתי לקבוע את השעון מעורר?",
            "alarm_label": alarm_label,
            "alarm_iso": None,
            "clarification_for": "time",
            "debug": {"intent": "alarm", "confidence": confidence, "reason": "missing_time"}
        }


def _decide_shopping(text: str, entities: dict, user_id: str, confidence: float) -> dict:
    """
    Decide what to do for shopping intent.
    
    Rules:
    - Extract items from entities or text
    - Always SUCCESS if items found
    - NEEDS_CLARIFICATION if no items detected
    
    CONTRACT for Shortcut:
    - items: List of individual shopping items
    - The Shortcut creates/appends to a note called "🛒 רשימת קניות"
    - Each item becomes a checklist line in Apple Notes
    """
    # Extract items from entities
    items_raw = entities.get("items", "")
    
    if items_raw:
        # Parse comma-separated items: "חלב, ביצים, לחם"
        items = [item.strip() for item in items_raw.split(",") if item.strip()]
    else:
        # Try to extract from text directly (fallback)
        items = []
    
    if items:
        action = {
            "type": ACTION_ADD_SHOPPING,
            "payload": {
                "items": items,
                "user_id": user_id
            }
        }
        
        items_display = ", ".join(items)
        feedback_msg = f"נוסף לרשימת קניות: {items_display}"
        
        return {
            "status": STATUS_SUCCESS,
            "actions": [action],
            "feedback": feedback_msg,
            "items": items,
            "debug": {"intent": "shopping", "confidence": confidence}
        }
    else:
        # No items detected
        return {
            "status": STATUS_NEEDS_CLARIFICATION,
            "actions": [],
            "feedback": "מה להוסיף לרשימת הקניות?",
            "items": [],
            "clarification_for": "items",
            "debug": {"intent": "shopping", "confidence": confidence, "reason": "missing_items"}
        }


def _decide_note(text: str, entities: dict, user_id: str, confidence: float) -> dict:
    """
    Decide what to do for note intent.
    
    Rules:
    - Always SUCCESS
    - CONTRACT: returns formatted_content ready for Apple Notes
    - NO side effects, NO validation
    """
    # Format the note content (this is the ONLY responsibility of the server for notes)
    # The client (Shortcut) expects: "Text... (DD/MM/YYYY HH:MM)"
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    formatted_content = f"{text}\n\n({now_str})"
    
    # We create a stub action just for internal tracking/logging if needed, 
    # but the REAL payload is the 'feedback' field which brain_dump_flow will use as 'message'.
    action = {
        "type": ACTION_SAVE_NOTE,
        "payload": {
            "content": text,
            "user_id": user_id,
            "note_type": "IDEAS",
            "formatted_content": formatted_content
        }
    }
    
    return {
        "status": STATUS_SUCCESS,
        "actions": [action],
        # CRITICAL: This feedback string IS the message payload for the shortcut
        "feedback": formatted_content,
        "debug": {"intent": "note", "confidence": confidence}
    }


def _decide_question(text: str, entities: dict, user_id: str, confidence: float) -> dict:
    """
    Decide what to do for question intent.
    
    Rules:
    - For Step 4: return SUCCESS but explain questions not implemented yet
    - Future: might integrate with search/knowledge base
    """
    return {
        "status": STATUS_SUCCESS,
        "actions": [action],
        "feedback": "I understand you have a question, but question handling is not implemented yet. / הבנתי שיש לך שאלה, אבל עדיין אין לי אפשרות לענות על שאלות. בינתיים אני יכול לעזור עם משימות ואירועים.",
        "debug": {"intent": "question", "confidence": confidence, "reason": "not_implemented"}
    }


def _decide_unknown(text: str, entities: dict, user_id: str, confidence: float) -> dict:
    """
    Decide what to do for unknown intent.
    
    Rules:
    - NEEDS_CLARIFICATION asking user to rephrase
    """
    return {
        "status": STATUS_NEEDS_CLARIFICATION,
        "actions": [],
        "feedback": "I didn't quite understand that. Could you rephrase? / לא לגמרי הבנתי אותך, אפשר לנסח מחדש? אני יכול לעזור לקבוע פגישות או לשמור משימות.",
        "debug": {"intent": "unknown", "confidence": confidence, "reason": "unclear_intent"}
    }
