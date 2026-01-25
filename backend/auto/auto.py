"""
auto/auto.py - Infrastructure and Configuration

═══════════════════════════════════════════════════════════════════════════════
PURPOSE: Infrastructure ONLY
═══════════════════════════════════════════════════════════════════════════════

This file exists to provide:
- Environment variable access
- Configuration loading
- Secret management
- System-level utilities

This file is "plumbing", not "brain".

═══════════════════════════════════════════════════════════════════════════════
ALLOWED (Infrastructure):
═══════════════════════════════════════════════════════════════════════════════

✅ Load environment variables
✅ Check if secrets exist
✅ Return configuration values
✅ Handle missing .env gracefully

═══════════════════════════════════════════════════════════════════════════════
NOT ALLOWED (Business Logic):
═══════════════════════════════════════════════════════════════════════════════

❌ Intent classification
❌ OpenAI API calls
❌ Decision rules
❌ Action execution
❌ User verification
❌ Any business logic

═══════════════════════════════════════════════════════════════════════════════
EXAMPLE:
═══════════════════════════════════════════════════════════════════════════════

Good:    get_openai_api_key() → returns the key
Bad:     classify_text_with_openai() → business logic, belongs in agent_process
"""

import os
from typing import Optional


def get_env_variable(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get an environment variable value.
    
    This is a UTILITY function for infrastructure only.
    
    Args:
        key (str): Environment variable name (e.g., "OPENAI_API_KEY")
        default (Optional[str]): Default value if not found
        required (bool): If True, raises error if variable is missing
        
    Returns:
        Optional[str]: The variable value, or default if not found
        
    Raises:
        ValueError: If required=True and variable is not set
        
    Example:
        >>> get_env_variable("OPENAI_API_KEY", required=True)
        "sk-..."
        
        >>> get_env_variable("OPTIONAL_SETTING", default="fallback")
        "fallback"
    """
    value = os.getenv(key, default)
    
    if required and value is None:
        raise ValueError(
            f"Required environment variable '{key}' is not set. "
            f"Please add it to your .env file."
        )
    
    return value


def get_openai_api_key() -> Optional[str]:
    """
    Get the OpenAI API key from environment variables.
    
    This is INFRASTRUCTURE: we just return the key.
    What to DO with the key is NOT this file's responsibility.
    
    Returns:
        Optional[str]: The OpenAI API key, or None if not set
        
    Example:
        >>> get_openai_api_key()
        "sk-proj-..."
        
    Note:
        - Looks for OPENAI_API_KEY in environment
        - Returns None if not found (graceful degradation)
        - Does NOT call OpenAI
        - Does NOT throw errors (lets caller decide what to do)
    """
    return get_env_variable("OPENAI_API_KEY", default=None, required=False)


def load_env_file():
    """
    Load environment variables from .env file.
    
    This makes development easier:
    - Create a .env file in the project root
    - Add secrets there (never commit to git!)
    - This function loads them into the environment
    
    Note:
        - Uses python-dotenv library (install: pip install python-dotenv)
        - Safe to call multiple times
        - Fails silently if .env doesn't exist (production uses real env vars)
        
    Example .env file:
        OPENAI_API_KEY=sk-proj-...
        DATABASE_URL=postgresql://...
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("[auto.py] Loaded environment variables from .env")
    except ImportError:
        # python-dotenv not installed - that's OK in production
        # where we use real environment variables
        pass
    except Exception as e:
        # .env file might not exist - that's OK
        print(f"[auto.py] Note: Could not load .env file: {e}")


# Auto-load .env when this module is imported
# This makes it "just work" for development
load_env_file()


# =============================================================================
# FUTURE INFRASTRUCTURE FUNCTIONS (add only when needed!)
# =============================================================================

# Examples of what MIGHT be added later (only if needed):
# - get_database_url() → returns DB connection string
# - get_supabase_config() → returns Supabase credentials
# - is_production() → returns True if running in production
# - get_log_level() → returns logging level from env
#
# Remember: INFRASTRUCTURE ONLY, no business logic!
