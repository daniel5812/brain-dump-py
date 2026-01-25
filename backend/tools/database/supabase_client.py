import os
from supabase import create_client, Client

# These will be loaded from environment variables on Render
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[Supabase] WARNING: SUPABASE_URL or SUPABASE_KEY not set. Persistence will fail.")
    supabase: Client = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[Supabase] Client initialized")
