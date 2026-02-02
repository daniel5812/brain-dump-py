import os
from supabase import create_client, Client

# These will be loaded from environment variables on Render
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().replace('"', '').replace("'", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip().replace('"', '').replace("'", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[Supabase] WARNING: SUPABASE_URL or SUPABASE_KEY not set. Persistence will fail.")
    supabase: Client = None
else:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"[Supabase] Client initialized (host: {SUPABASE_URL.split('//')[-1].split('/')[0]})")
    except Exception as e:
        print(f"[Supabase] ERROR during initialization: {e}")
        supabase = None
