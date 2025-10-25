# /Users/brandonnguyen/Projects/ai-block-bookkeeper/backend/config/database.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseConfig:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not all([self.url, self.anon_key]):
            raise ValueError("Missing required Supabase environment variables")
    
    def get_client(self, use_service_role: bool = False) -> Client:
        """Get Supabase client instance"""
        key = self.service_role_key if use_service_role else self.anon_key
        
        # Simple initialization for supabase 1.0.4
        return create_client(self.url, key)

# Global instance
supabase_config = SupabaseConfig()