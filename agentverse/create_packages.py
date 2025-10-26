#!/usr/bin/env python3
"""
Simple Railway Deployment Helper
Creates individual deployment packages for each agent
"""

import os
import shutil
from pathlib import Path

def create_deployment_packages():
    """Create individual deployment packages"""
    
    agents = [
        {
            "name": "audit-agent",
            "file": "audit_verification_agent.py",
            "description": "Audit Verification Agent"
        },
        {
            "name": "document-agent", 
            "file": "document_processing_agent.py",
            "description": "Document Processing Agent"
        },
        {
            "name": "reconciliation-agent",
            "file": "reconciliation_agent.py", 
            "description": "Reconciliation Agent"
        }
    ]
    
    print("🚀 Creating Railway Deployment Packages")
    print("=" * 50)
    
    for agent in agents:
        print(f"\n📦 Creating {agent['name']} package...")
        
        # Create directory
        agent_dir = Path(agent['name'])
        agent_dir.mkdir(exist_ok=True)
        
        # Create Procfile
        procfile_content = f"web: python {agent['file']}"
        with open(agent_dir / "Procfile", "w") as f:
            f.write(procfile_content)
        
        # Create requirements.txt
        requirements_content = """uagents
python-dotenv
anthropic
supabase
structlog
pydantic
httpx
"""
        with open(agent_dir / "requirements.txt", "w") as f:
            f.write(requirements_content)
        
        # Create railway.json
        railway_config = f"""{{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {{
    "builder": "NIXPACKS"
  }},
  "deploy": {{
    "startCommand": "python {agent['file']}",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }}
}}"""
        with open(agent_dir / "railway.json", "w") as f:
            f.write(railway_config)
        
        # Copy agent file
        shutil.copy2(agent["file"], agent_dir / agent["file"])
        
        print(f"✅ Created {agent['name']}/ with:")
        print(f"   - Procfile: {procfile_content}")
        print(f"   - requirements.txt")
        print(f"   - railway.json")
        print(f"   - {agent['file']}")
    
    print("\n🎯 Next Steps:")
    print("1. Go to https://railway.app")
    print("2. Sign up with GitHub")
    print("3. Create 3 new projects:")
    print("   - Deploy from GitHub repo")
    print("   - Select your ai-block-bookkeeper repository")
    print("   - Set Root Directory to:")
    print("     • agentverse/audit-agent")
    print("     • agentverse/document-agent") 
    print("     • agentverse/reconciliation-agent")
    print("4. Deploy each project")
    print("5. Get your public URLs!")

if __name__ == "__main__":
    create_deployment_packages()
