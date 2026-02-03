
import sys
import os
from unittest.mock import patch, MagicMock

# Add backend to path - Assuming we run from project root
sys.path.append(os.path.abspath('backend'))

from tools.business_logic.brain_dump_flow import brain_dump_flow
from tools.decision.decision_engine import decide

def test_notes_contract():
    print("=== Testing Notes Contract ===")
    
    # Mock input
    user_id = "test_user"
    original_text = "This is a test note"
    
    # Mock agent response
    mock_agent_result = {
        "intent": "note",
        "confidence": 0.99,
        "entities": {},
        "original_text": original_text
    }
    
    # Patch agent_process.process_text so we don't hit OpenAI
    with patch('tools.agent.agent_process.process_text', return_value=mock_agent_result) as mock_process:
        
        # Run the flow
        result = brain_dump_flow(original_text, user_id)
        
        print(f"\nResult received: {result}")
        
        # Verify strict contract
        assert result.get("status") == "SUCCESS", "Status must be SUCCESS"
        assert result.get("intent") == "note", "Intent must be 'note'"
        assert "message" in result, "Message field is required"
        assert original_text in result["message"], "Message should contain original text"
        assert "(" in result["message"] and ")" in result["message"], "Message should likely contain timestamp in parens"
        
        # Verify no extra fields like 'action_taken' or 'debug' in top level for notes
        # The contract said: "No extra fields."
        # The result from brain_dump_flow returns checking keys.
        
        allowed_keys = {"status", "intent", "message"}
        actual_keys = set(result.keys())
        extra_keys = actual_keys - allowed_keys
        
        if extra_keys:
            print(f"WARNING: Found extra keys violating contract: {extra_keys}")
            # Depending on strictness, we might want to fail. The user said "No extra fields."
            # My implementation returns EXCACTLY the dict with those 3 keys.
            assert not extra_keys, f"Contract violation: Extra keys found {extra_keys}"
            
        print("\n✅ Contract Verified!")
        print(f"Message content: {result['message']}")

if __name__ == "__main__":
    test_notes_contract()
