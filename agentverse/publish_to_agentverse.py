#!/usr/bin/env python3
"""
Agentverse Publishing Script
Publish AI Block Bookkeeper agents to Agentverse platform
"""

import json
import logging
import requests
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agentverse API configuration
AGENTVERSE_API_BASE = "https://api.agentverse.ai"
AGENTVERSE_WEB_BASE = "https://agentverse.ai"

def create_agent_registration_data():
    """Create registration data for all agents"""
    agents = [
        {
            "name": "AuditVerificationAgent",
            "display_name": "Audit Verification Agent",
            "description": "AI-Powered Blockchain Transaction Auditor for Financial Documents. Posts financial transactions to Sui blockchain for immutable audit trails.",
            "category": "Finance",
            "tags": ["blockchain", "audit", "verification", "financial", "transactions", "sui", "immutable", "audit-trail"],
            "capabilities": [
                "Blockchain transaction posting",
                "Document hash verification", 
                "Immutable audit trail creation",
                "Transaction integrity checking",
                "ASI:One Chat Protocol support"
            ],
            "readme_file": "README_audit_verification_agent.md",
            "agent_file": "audit_verification_agent.py",
            "port": 8001
        },
        {
            "name": "DocumentProcessingAgent",
            "display_name": "Document Processing Agent", 
            "description": "AI-Powered Financial Document Analyzer and Business Event Generator. Extracts structured data from invoices, receipts, and financial documents using Claude AI.",
            "category": "Finance",
            "tags": ["document-processing", "ai-extraction", "financial-documents", "invoice-processing", "claude-ai", "pdf", "csv"],
            "capabilities": [
                "AI-powered document extraction",
                "Multi-format support (PDF, CSV, Excel, Images)",
                "Business event generation",
                "Multi-agent coordination",
                "ASI:One Chat Protocol support"
            ],
            "readme_file": "README_document_processing_agent.md",
            "agent_file": "document_processing_agent.py",
            "port": 8003
        },
        {
            "name": "ReconciliationAgent",
            "display_name": "Reconciliation Agent",
            "description": "Automated Financial Transaction Matcher and Reconciliation Engine. Automatically matches invoices to payments and creates reconciliation records.",
            "category": "Finance", 
            "tags": ["reconciliation", "transaction-matching", "invoice-matching", "payment-reconciliation", "financial-matching", "automation"],
            "capabilities": [
                "Automatic invoice-to-payment matching",
                "Reference number matching",
                "Amount tolerance handling",
                "Confidence scoring",
                "Discrepancy detection and flagging",
                "ASI:One Chat Protocol support"
            ],
            "readme_file": "README_reconciliation_agent.md",
            "agent_file": "reconciliation_agent.py",
            "port": 8004
        }
    ]
    
    return agents

def check_agent_files():
    """Check if all required agent files exist"""
    required_files = [
        "audit_verification_agent.py",
        "document_processing_agent.py", 
        "reconciliation_agent.py",
        "README_audit_verification_agent.md",
        "README_document_processing_agent.md",
        "README_reconciliation_agent.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
        return False
    
    logger.info("✓ All required agent files are present")
    return True

def register_agent_on_agentverse(agent_data):
    """Register a single agent on Agentverse"""
    logger.info(f"Registering {agent_data['display_name']}...")
    
    # Prepare registration payload
    payload = {
        "name": agent_data["name"],
        "display_name": agent_data["display_name"],
        "description": agent_data["description"],
        "category": agent_data["category"],
        "tags": agent_data["tags"],
        "capabilities": agent_data["capabilities"],
        "protocols": ["ASI_CHAT_PROTOCOL"],
        "status": "active",
        "visibility": "public"
    }
    
    try:
        # Register agent (this is a mock - replace with actual Agentverse API)
        logger.info(f"📤 Sending registration request for {agent_data['name']}")
        logger.info(f"   Description: {agent_data['description']}")
        logger.info(f"   Category: {agent_data['category']}")
        logger.info(f"   Tags: {', '.join(agent_data['tags'])}")
        
        # TODO: Replace with actual Agentverse API call
        # response = requests.post(f"{AGENTVERSE_API_BASE}/agents", json=payload)
        
        logger.info(f"✅ {agent_data['display_name']} registration prepared")
        logger.info(f"   Agent file: {agent_data['agent_file']}")
        logger.info(f"   README: {agent_data['readme_file']}")
        logger.info(f"   Port: {agent_data['port']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to register {agent_data['name']}: {str(e)}")
        return False

def print_manual_registration_instructions():
    """Print manual registration instructions"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("📋 MANUAL REGISTRATION INSTRUCTIONS")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Since Agentverse API registration requires authentication,")
    logger.info("here's how to manually register your agents:")
    logger.info("")
    logger.info("1. 🌐 Go to Agentverse Platform:")
    logger.info(f"   {AGENTVERSE_WEB_BASE}")
    logger.info("")
    logger.info("2. 🔐 Sign up/Login to your account")
    logger.info("")
    logger.info("3. ➕ Click 'Create New Agent' or 'Add Agent'")
    logger.info("")
    logger.info("4. 📝 For each agent, provide:")
    logger.info("")
    
    agents = create_agent_registration_data()
    for i, agent in enumerate(agents, 1):
        logger.info(f"   Agent {i}: {agent['display_name']}")
        logger.info(f"   - Name: {agent['name']}")
        logger.info(f"   - Description: {agent['description']}")
        logger.info(f"   - Category: {agent['category']}")
        logger.info(f"   - Tags: {', '.join(agent['tags'])}")
        logger.info(f"   - Agent File: Upload {agent['agent_file']}")
        logger.info(f"   - README: Upload {agent['readme_file']}")
        logger.info("")
    
    logger.info("5. 🚀 Deploy your agents:")
    logger.info("   - Use Agentverse's cloud infrastructure")
    logger.info("   - Or provide your own server endpoints")
    logger.info("")
    logger.info("6. ✅ Test your agents:")
    logger.info("   - Use Agentverse's testing interface")
    logger.info("   - Send ChatMessage requests")
    logger.info("   - Verify health endpoints")
    logger.info("")

def main():
    """Main publishing function"""
    logger.info("🚀 AI Block Bookkeeper - Agentverse Publishing")
    logger.info("=" * 50)
    
    # Check prerequisites
    if not check_agent_files():
        logger.error("❌ Missing required files")
        sys.exit(1)
    
    # Get agent data
    agents = create_agent_registration_data()
    
    logger.info(f"📦 Found {len(agents)} agents ready for publishing")
    logger.info("")
    
    # Register each agent
    success_count = 0
    for agent in agents:
        if register_agent_on_agentverse(agent):
            success_count += 1
    
    logger.info("")
    logger.info(f"📊 Registration Summary: {success_count}/{len(agents)} agents prepared")
    
    if success_count == len(agents):
        logger.info("✅ All agents ready for Agentverse publishing!")
        print_manual_registration_instructions()
    else:
        logger.error("❌ Some agents failed registration")
        sys.exit(1)

if __name__ == "__main__":
    main()
