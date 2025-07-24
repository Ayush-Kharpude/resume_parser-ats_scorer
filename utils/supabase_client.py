import streamlit as st
import os
from supabase import create_client, Client

# Secure credential loading
try:
    # For Streamlit Cloud
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
except (KeyError, FileNotFoundError):
    # For local development
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError(
            "Supabase credentials not found. "
            "Please set SUPABASE_URL and SUPABASE_KEY environment variables "
            "or configure Streamlit secrets."
        )

supabase: Client = create_client(url, key)
