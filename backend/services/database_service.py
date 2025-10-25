# /Users/brandonnguyen/Projects/ai-block-bookkeeper/backend/services/database_service.py
from typing import Optional, Dict, Any, List
from supabase import Client
from config.database import supabase_config
import structlog

logger = structlog.get_logger()

class DatabaseService:
    def __init__(self, use_service_role: bool = False):
        self.client: Client = supabase_config.get_client(use_service_role)
        self.logger = logger.bind(service="database")
    
    async def create_business_event(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new business event"""
        try:
            result = self.client.table("business_events").insert(event_data).execute()
            self.logger.info("Business event created", event_id=event_data.get("event_id"))
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error("Failed to create business event", error=str(e))
            raise
    
    async def get_business_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a business event by ID"""
        try:
            result = self.client.table("business_events").select("*").eq("event_id", event_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error("Failed to get business event", event_id=event_id, error=str(e))
            raise
    
    async def create_journal_entry(self, entry_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new journal entry"""
        try:
            result = self.client.table("journal_entries").insert(entry_data).execute()
            self.logger.info("Journal entry created", entry_id=entry_data.get("entry_id"))
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error("Failed to create journal entry", error=str(e))
            raise
    
    async def create_party(self, party_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new party"""
        try:
            result = self.client.table("parties").insert(party_data).execute()
            self.logger.info("Party created", party_id=party_data.get("party_id"))
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error("Failed to create party", error=str(e))
            raise
    
    async def create_audit_log(self, log_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create an audit log entry"""
        try:
            result = self.client.table("audit_logs").insert(log_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error("Failed to create audit log", error=str(e))
            raise
    
    async def get_events_by_source(self, source_system: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get business events by source system"""
        try:
            result = self.client.table("business_events")\
                .select("*")\
                .eq("source_system", source_system)\
                .order("recorded_at", desc=True)\
                .limit(limit)\
                .execute()
            return result.data or []
        except Exception as e:
            self.logger.error("Failed to get events by source", source_system=source_system, error=str(e))
            raise

# Global service instance
db_service = DatabaseService()