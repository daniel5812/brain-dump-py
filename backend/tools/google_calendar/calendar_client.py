import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CalendarClient:
    def __init__(self):
        # Using full calendar scope to allow creating and managing events
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self.creds = self._load_credentials()
        self.service = build('calendar', 'v3', credentials=self.creds)

    def _load_credentials(self):
        # 1. Try loading from a JSON environment variable (preferred for Render)
        json_content = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        
        if json_content:
            try:
                print("[CalendarClient] FOUND GOOGLE_SERVICE_ACCOUNT_JSON env var. Attempting to parse...")
                info = json.loads(json_content)
                return service_account.Credentials.from_service_account_info(
                    info, scopes=self.scopes)
            except Exception as e:
                print(f"[CalendarClient] ERROR parsing GOOGLE_SERVICE_ACCOUNT_JSON: {e}")
        else:
            print("[CalendarClient] WARNING: GOOGLE_SERVICE_ACCOUNT_JSON env var is NOT set or EMPTY.")

        # 2. Fallback to local file for development
        key_filename = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", "brain-dump-484011-7dc82cec457d.json")
        
        # Look for the file in the same directory as this script, or the backend root
        current_dir = os.path.dirname(os.path.abspath(__file__)) # tools/google_calendar
        backend_dir = os.path.dirname(os.path.dirname(current_dir)) # backend root
        json_path = os.path.join(backend_dir, key_filename)
        
        print(f"[CalendarClient] Attempting fallback to local file: {json_path}")
        
        if not os.path.exists(json_path):
            # Debug: Print which env vars ARE present (just keys)
            print(f"[CalendarClient] Debug - Available Env Vars: {list(os.environ.keys())}")
            if json_content: # If we HAD env var but parsing failed
                 raise RuntimeError("Failed to load credentials from BOTH env var and local file.")
            raise FileNotFoundError(f"Service account key not found at {json_path} and GOOGLE_SERVICE_ACCOUNT_JSON is missing.")
            
        return service_account.Credentials.from_service_account_file(
            json_path, scopes=self.scopes)


    def verify_access(self, calendar_id: str) -> bool:
        """
        Check if we have access to the specified calendar.
        """
        try:
            print(f"[CalendarClient] Verifying access to: {calendar_id}")
            self.service.calendars().get(calendarId=calendar_id).execute()
            print(f"[CalendarClient] Access verified for {calendar_id}")
            return True
        except HttpError as e:
            print(f"[CalendarClient] Access check failed for {calendar_id}: {e.resp.status}")
            return False
        except Exception as e:
            print(f"[CalendarClient] Unexpected error during verification: {e}")
            return False

    def create_event(self, calendar_id: str, title: str, start_iso: str, end_iso: str = None, description: str = "") -> dict:
        """
        Create an event in the user's calendar.
        
        Args:
            calendar_id: Usually the user's email
            title: Event title
            start_iso: Start time in ISO 8601 format (e.g. 2024-05-01T10:00:00Z)
            end_iso: Optional end time. If missing, defaults to 1 hour after start.
            description: Optional description
        """
        try:
            # If no end time provided, default to 1 hour after start
            if not end_iso:
                from datetime import datetime, timedelta
                start_dt = datetime.fromisoformat(start_iso.replace('Z', '+00:00'))
                end_iso = (start_dt + timedelta(hours=1)).isoformat()

            event = {
                'summary': title,
                'description': description,
                'start': {'dateTime': start_iso},
                'end': {'dateTime': end_iso},
            }

            print(f"[CalendarClient] Creating event '{title}' for {calendar_id}")
            created_event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            return {"ok": True, "event_id": created_event.get('id'), "link": created_event.get('htmlLink')}
            
        except Exception as e:
            print(f"[CalendarClient] Error creating event: {e}")
            return {"ok": False, "error": str(e)}

# Singleton instance
calendar_client = CalendarClient()
