"""
tools/business_logic/brain_dump_flow.py - Brain Dump Orchestration

RESPONSIBILITY:
- Orchestrate the ENTIRE brain dump flow from start to finish
- This is the "brain" of the system

WHY THIS FILE EXISTS:
- Single source of truth for business logic
- Endpoints know NOTHING about intents, decisions, or actions
- All the magic happens here

STRICT RULES:
✅ Orchestration logic
✅ Call agent_process for intent classification
✅ Call action executors
✅ Return feedback

❌ NO HTTP knowledge (FastAPI, requests, responses)
❌ NO endpoint logic
❌ NO direct database access (use CRUD layer)

THE FULL FLOW (when complete):
1. Receive transcribed text + user_id
2. Call agent_process to classify intent
3. Extract entities (e.g., "milk" from "add milk to shopping list")
4. Apply decision rules (which action to take?)
5. Execute the action (add to Todoist, create calendar event, etc.)
6. Generate feedback for the user
7. Return result

CURRENT STATE (Step 2):
- Stub implementation: echo back the input
- No intent classification yet
- No action execution yet
- Just proves the flow works

FUTURE ENHANCEMENTS (Later Steps):
- Real intent classification (Step 3+)
- Entity extraction
- Action execution (Todoist, Calendar, Email)
- Smart feedback generation
"""


def brain_dump_flow(text: str, user_id: str) -> dict:
    """
    Orchestrate the entire brain dump flow.
    
    This is the CORE of the Brain Dump system.
    This function is PURELY ORCHESTRATION - it calls other components but contains NO logic itself.
    
    Flow (Step 4):
    1. Agent: Classify intent from text
    2. Decision: Validate and create action plan
    3. Execute: Run actions (stub for now)
    4. Respond: Return status + feedback to user
    
    Args:
        text (str): The transcribed voice message from the user
        user_id (str): The verified user's ID (already passed security gate)
        
    Returns:
        dict: Result containing:
            - success (bool): Whether the flow completed successfully
            - message (str): Human-readable feedback for the user
            - action_taken (str or None): Summary of what action was executed
            - status (str): Decision status (SUCCESS / NEEDS_CLARIFICATION / etc.)
            - debug (dict): Debug information (optional)
            
    Example:
        >>> brain_dump_flow("Add milk to shopping list", "daniel")
        {
            "success": True,
            "message": "I'll add this task for you: 'Add milk to shopping list'",
            "action_taken": "CREATE_TASK: STUB executed",
            "status": "SUCCESS"
        }
    """
    # =========================================================================
    # STEP 1: AGENT - Classify Intent
    # =========================================================================
    
    from tools.agent.agent_process import process_text
    
    print(f"[brain_dump_flow] === Starting flow for: '{text}' ===")
    print(f"[brain_dump_flow] Step 1: Calling agent to classify intent...")
    
    intent_result = process_text(text)
    
    print(f"[brain_dump_flow] Agent returned:")
    print(f"  - intent: {intent_result['intent']}")
    print(f"  - confidence: {intent_result['confidence']}")
    print(f"  - entities: {intent_result['entities']}")
    
    # =========================================================================
    # STEP 2: DECISION - Validate and Create Action Plan
    # =========================================================================
    
    from tools.decision.decision_engine import decide
    
    print(f"[brain_dump_flow] Step 2: Calling decision engine...")
    
    decision = decide(intent_result, user_id)
    
    print(f"[brain_dump_flow] Decision engine returned:")
    print(f"  - status: {decision['status']}")
    print(f"  - actions: {len(decision['actions'])} action(s)")
    print(f"  - feedback: {decision['feedback']}")
    
    # =========================================================================
    # STEP 3: EXECUTE - Run Actions (if any)
    # =========================================================================
    
    execution_results = []
    action_summary = None
    
    if decision['actions']:
        from tools.actions.action_executor import execute
        
        print(f"[brain_dump_flow] Step 3: Executing {len(decision['actions'])} action(s)...")
        
        execution_results = execute(decision['actions'], user_id)
        
        # Summarize what was executed
        action_types = [result['type'] for result in execution_results if result.get('ok')]
        if action_types:
            action_summary = f"{', '.join(action_types)}"
        
        print(f"[brain_dump_flow] Execution complete: {len(execution_results)} result(s)")
    else:
        print(f"[brain_dump_flow] Step 3: No actions to execute (clarification/validation needed)")
    
    # =========================================================================
    # STEP 4: RESPOND - Format Response for User
    # =========================================================================
    
    # SPECIAL HANDLING FOR NOTES (Contract Check)
    # If intent is 'note', we MUST return the strict JSON format and bypass standard flow
    if intent_result.get('intent') == 'note':
        print(f"[brain_dump_flow] Note intent detected. Returning strict JSON contract.")
        return {
            "status": "SUCCESS",
            "intent": "note",
            "message": decision['feedback']  # Use the formatted text from decision engine
        }
    
    # SPECIAL HANDLING FOR REMINDERS (Contract Check)
    # Similar to notes - return strict JSON format for the Shortcut to process
    if intent_result.get('intent') == 'reminder':
        print(f"[brain_dump_flow] Reminder intent detected. Returning strict JSON contract.")
        
        # Format reminder_time like notes: (HH:MM DD/MM/YYYY)
        reminder_time_formatted = None
        if decision.get('reminder_time'):
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(decision['reminder_time'])
                reminder_time_formatted = dt.strftime("(%H:%M %d/%m/%Y)")
            except:
                reminder_time_formatted = decision['reminder_time']
        
        return {
            "status": decision['status'],  # SUCCESS or NEEDS_CLARIFICATION
            "intent": "reminder",
            "message": decision['feedback'],
            "reminder_title": decision.get('reminder_title'),
            "reminder_time": reminder_time_formatted,  # Formatted like (19:17 05/02/2026)
            "clarification_for": decision.get('clarification_for')  # "time" when missing
        }
    
    # Determine overall success
    # SUCCESS status means we did something successfully
    # Other statuses mean we need user input or something failed
    success = decision['status'] == "SUCCESS"
    
    print(f"[brain_dump_flow] === Flow complete ===")
    print(f"  - Overall success: {success}")
    print(f"  - Status: {decision['status']}")
    
    return {
        "success": success,
        "message": decision['feedback'],
        "action_taken": action_summary,
        "status": decision['status'],
        "debug": {
            "intent": intent_result['intent'],
            "confidence": intent_result['confidence'],
            "num_actions": len(decision['actions']),
            "execution_results": execution_results if execution_results else None
        }
    }
    
    # =========================================================================
    # FUTURE ENHANCEMENTS (Step 5+)
    # =========================================================================
    # - Real action execution (Todoist, Calendar, etc.)
    # - Error handling for execution failures
    # - Retry logic
    # - User preferences (default project, calendar, etc.)
    # - Smart feedback based on execution results

