"""
tools/agent/agent_process.py - Agent Layer (Intent Classification)

═══════════════════════════════════════════════════════════════════════════════
RESPONSIBILITY
═══════════════════════════════════════════════════════════════════════════════

This file is the AGENT LAYER.

Input:  Raw text (from voice-to-text)
Output: Structured understanding (intent + entities)

This file does NOT know about:
- HTTP / FastAPI
- Users / Authentication
- Actions / Execution
- Database

═══════════════════════════════════════════════════════════════════════════════
THE CONTRACT (IMMUTABLE)
═══════════════════════════════════════════════════════════════════════════════

def process_text(text: str) -> dict

Returns ALWAYS this structure:
{
    "intent": str,         # One of: task/event/reminder/note/question/unknown
    "confidence": float,   # 0.0 to 1.0
    "entities": dict,      # Extracted information (can be {})
    "original_text": str   # Echo back the input
}

This contract NEVER changes, even if we:
- Replace OpenAI with Anthropic
- Replace OpenAI with Gemini
- Replace OpenAI with rule-based logic
- Remove AI completely

═══════════════════════════════════════════════════════════════════════════════
INTENT CATEGORIES (CLOSED SET - DO NOT MODIFY)
═══════════════════════════════════════════════════════════════════════════════

These are the ONLY valid intents in the system.
This is the shared language between all components.
"""

import os
import re
from typing import Optional, Dict

# Intent categories - closed set, do not add without architectural review
VALID_INTENTS = {
    "task",      # User wants to add a todo/task (e.g., "add milk to shopping list")
    "event",     # User wants to create a calendar event (e.g., "schedule meeting tomorrow")
    "reminder",  # User wants to set a reminder (e.g., "remind me to call mom")
    "alarm",     # User wants to set an alarm (e.g., "set alarm in 17 minutes", "wake me up at 7")
    "note",      # User wants to save a note/idea (e.g., "note: great idea for the project")
    "question",  # User is asking a question (e.g., "what's the weather?")
    "unknown"    # Cannot determine intent (fallback)
}


def process_text(text: str) -> dict:
    """
    Process raw text and return structured intent understanding.
    
    This is the MAIN CONTRACT of the agent layer.
    External callers use ONLY this function.
    
    IMPLEMENTATION (Phase C - OpenAI):
    - Calls OpenAI to classify intent
    - Uses structured prompt with clear intent categories
    - Handles errors gracefully (fallback to "unknown")
    - Maintains the SAME contract as the stub
    
    Args:
        text (str): Raw user input from voice-to-text
        
    Returns:
        dict: Structured result with this EXACT schema:
            {
                "intent": str,         # One of VALID_INTENTS
                "confidence": float,   # 0.0 to 1.0 (how sure we are)
                "entities": dict,      # Extracted info (e.g., {"item": "milk"})
                "original_text": str   # The input text (for logging/debugging)
            }
            
    Example:
        >>> process_text("Add milk to shopping list")
        {
            "intent": "task",
            "confidence": 0.95,
            "entities": {"item": "milk", "list": "shopping"},
            "original_text": "Add milk to shopping list"
        }
    """
    from auto.auto import get_openai_api_key
    
    # Get API key from infrastructure layer
    api_key = get_openai_api_key()
    
    if not api_key:
        # No API key available - graceful degradation
        print("[agent_process] WARNING: No OpenAI API key found, falling back to unknown intent")
        return _fallback_intent(text)
    
    try:
        # Import OpenAI client
        from openai import OpenAI
        
        # Initialize client
        client = OpenAI(api_key=api_key)
        
        # Build the prompt
        prompt = _build_prompt(text)
        
        print(f"[agent_process] Calling OpenAI to classify: '{text}'")
        
        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Good balance of cost/speed/quality
            messages=[
                {"role": "system", "content": "You are an assistant for 'Brain Dump'. You help users capture tasks, events, and notes. You MUST support both Hebrew and English. If the user speaks Hebrew, analyze the intent correctly in Hebrew."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Low temperature for consistent classification
            max_tokens=150
        )
        
        # Extract response
        result_text = response.choices[0].message.content.strip()
        
        # Parse the response
        intent_result = _parse_openai_response(result_text, text)
        
        print(f"[agent_process] OpenAI classified as: {intent_result['intent']} (confidence: {intent_result['confidence']})")
        
        return intent_result
        
    except Exception as e:
        # Something went wrong - fallback gracefully
        print(f"[agent_process] ERROR during OpenAI classification: {e}")
        print(f"[agent_process] Falling back to unknown intent")
        return _fallback_intent(text)


# =============================================================================
# PRIVATE HELPER FUNCTIONS (Phase C)
# =============================================================================

def _build_prompt(text: str) -> str:
    """
    Build the OpenAI prompt for intent classification.
    
    This is PRIVATE (internal implementation detail).
    
    Args:
        text: User's raw input
        
    Returns:
        str: Formatted prompt for OpenAI
    """
    return f"""Classify the following user message into ONE of these intents:

Intents:
- task: User wants to add a todo/task (e.g., "add milk to list", "buy groceries", "remember to call")
- event: User wants to create a calendar event (e.g., "schedule meeting tomorrow", "set appointment")
- reminder: User wants to set a reminder about something (e.g., "remind me to call mom", "תזכיר לי לאסוף את המשלוח")
- alarm: User explicitly wants to set an ALARM / clock alarm (e.g., "שעון מעורר", "תעיר אותי", "set alarm", "אלארם"). Use this ONLY when the user explicitly says alarm/שעון מעורר/תעיר אותי.
- note: User wants to save a note/idea (e.g., "note: great idea", "save this thought")
- question: User is asking a question (e.g., "what's the weather?", "how do I...?")
- unknown: Cannot determine clear intent

User message: "{text}"
Language Note: The user may speak Hebrew, English, or both. Transliterate or translate entities if necessary, but keep the core meaning. If it's an event, analyze the Hebrew temporal expressions (e.g. 'מחר' = tomorrow).
Current Local Time: {os.getenv("CURRENT_TIME_CONTEXT", "2026-01-25T21:30:00")}

Respond in this EXACT format:
Intent: <one of the above intents>
Confidence: <number between 0.0 and 1.0>
Entities: <extracted info: key="value", key="value">
- For 'event' or 'reminder': ONLY include start_iso (ISO 8601 format) and end_iso if the user EXPLICITLY mentions a date or time. If the user does NOT mention when, do NOT invent or guess a time — leave start_iso and end_iso out entirely.
- For 'alarm': include start_iso (ISO 8601 format) for the alarm time, and label (the reason/description, if mentioned). If no label is given, set label="".
- For 'task', include title and priority.

Example response:
Intent: event
Confidence: 0.98
Entities: title="Meeting with Boss", start_iso="2026-01-26T09:00:00", end_iso="2026-01-26T10:00:00"
"""


def _parse_openai_response(response_text: str, original_text: str) -> dict:
    """
    Parse OpenAI's response into our contract format.
    
    This is PRIVATE (internal implementation detail).
    
    Args:
        response_text: Raw response from OpenAI
        original_text: The user's original input
        
    Returns:
        dict: Parsed result matching our contract
    """
    try:
        # Parse the response (simple line-by-line parsing)
        lines = response_text.strip().split('\n')
        
        intent = "unknown"
        confidence = 0.5
        entities = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith("Intent:"):
                intent = line.split(":", 1)[1].strip().lower()
                # Validate it's a known intent
                if intent not in VALID_INTENTS:
                    intent = "unknown"
            elif line.startswith("Confidence:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                    # Clamp to 0.0-1.0
                    confidence = max(0.0, min(1.0, confidence))
                except:
                    confidence = 0.5
            elif line.startswith("Entities:"):
                entity_str = line.split(":", 1)[1].strip()
                if entity_str.lower() != "none":
                    # Simple key="value" parser
                    import re
                    matches = re.findall(r'(\w+)="([^"]*)"', entity_str)
                    if matches:
                        entities = {k: v for k, v in matches}
                    else:
                        entities = {"raw": entity_str}
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "original_text": original_text
        }
        
    except Exception as e:
        print(f"[agent_process] ERROR parsing OpenAI response: {e}")
        return _fallback_intent(original_text)


def _fallback_intent(text: str) -> dict:
    """
    Fallback intent when OpenAI fails or is unavailable.
    
    This is PRIVATE (internal implementation detail).
    
    Args:
        text: User's original input
        
    Returns:
        dict: Safe fallback result
    """
    return {
        "intent": "unknown",
        "confidence": 0.0,
        "entities": {},
        "original_text": text
    }

