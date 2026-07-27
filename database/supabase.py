"""
database/supabase.py

Single, shared Supabase client instance.
This is the ONLY module that should import the Supabase SDK directly.
Every other module (services, actions, routes) must import `supabase`
from here rather than creating its own client.
"""

import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()  # reads .env in the project root, if present

SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str | None = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError(
        "SUPABASE_URL and SUPABASE_KEY environment variables must be set. "
        "Add them to your .env file or your deployment environment."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_KEY:", os.getenv("SUPABASE_KEY")[:20] + "...")