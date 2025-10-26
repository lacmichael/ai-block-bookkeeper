#!/usr/bin/env python3
"""
Railway Deployment Script
Deploy AI Block Bookkeeper agents to Railway for public endpoints
"""

import os
import subprocess
import sys
from pathlib import Path

def create_railway_config():
    """Create Railway configuration files"""
    
    # Create railway.json for each agent
    agents = [
        {
            "name": "audit-agent",
            "file": "audit_verification_agent.py",
            "port": 8001,
            "description": "Audit Verification Agent"
        },
        {
            "name": "document-agent", 
            "file": "document_processing_agent.py",
            "port": 8003,
            "description": "Document Processing Agent"
        },
        {
            "name": "reconciliation-agent",
            "file": "reconciliation_agent.py", 
            "port": 8004,
            "description": "Reconciliation Agent"
        }
    ]
    
    for agent in agents:
        # Create directory if it doesn't exist
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
        
        # Copy agent file
        import shutil
        shutil.copy2(agent["file"], agent_dir / agent["file"])
        
        print(f"✅ Created {agent['name']}/ directory with:")
        print(f"   - Procfile: {procfile_content}")
        print(f"   - requirements.txt")
        print(f"   - {agent['file']}")
        print()

def print_railway_instructions():
    """Print Railway deployment instructions"""
    print("🚀 Railway Deployment Instructions")
    print("=" * 50)
    print()
    print("1. 🌐 Go to Railway: https://railway.app")
    print("2. 🔐 Sign up with GitHub")
    print("3. ➕ Click 'New Project'")
    print("4. 📁 Select 'Deploy from GitHub repo'")
    print("5. 🔗 Connect your GitHub account")
    print("6. 📂 Select your 'ai-block-bookkeeper' repository")
    print()
    print("For each agent:")
    print("7. 🆕 Create 3 separate Railway projects:")
    print("   - audit-agent")
    print("   - document-agent") 
    print("   - reconciliation-agent")
    print()
    print("8. ⚙️ Configure each project:")
    print("   - Root Directory: agentverse/audit-agent/")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: python audit_verification_agent.py")
    print()
    print("9. 🚀 Deploy each project")
    print("10. 🔗 Get public URLs:")
    print("    - https://audit-agent-production.up.railway.app")
    print("    - https://document-agent-production.up.railway.app")
    print("    - https://reconciliation-agent-production.up.railway.app")
    print()
    print("11. 📝 Update Agentverse with these public URLs")

def create_vercel_config():
    """Create Vercel configuration"""
    vercel_config = {
        "version": 2,
        "builds": [
            {
                "src": "audit_verification_agent.py",
                "use": "@vercel/python"
            },
            {
                "src": "document_processing_agent.py", 
                "use": "@vercel/python"
            },
            {
                "src": "reconciliation_agent.py",
                "use": "@vercel/python"
            }
        ],
        "routes": [
            {
                "src": "/audit/(.*)",
                "dest": "audit_verification_agent.py"
            },
            {
                "src": "/document/(.*)",
                "dest": "document_processing_agent.py"
            },
            {
                "src": "/reconciliation/(.*)",
                "dest": "reconciliation_agent.py"
            }
        ]
    }
    
    import json
    with open("vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)
    
    print("✅ Created vercel.json for multi-agent deployment")

def main():
    """Main deployment preparation"""
    print("🚀 Public Endpoint Deployment Preparation")
    print("=" * 50)
    print()
    
    # Check if we're in the right directory
    if not Path("audit_verification_agent.py").exists():
        print("❌ Please run this script from the agentverse/ directory")
        sys.exit(1)
    
    print("📋 Choose your deployment platform:")
    print("1. Railway (Recommended - Easiest)")
    print("2. Render (Free tier)")
    print("3. Heroku (Classic)")
    print("4. Vercel (Fast)")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🚂 Preparing Railway deployment...")
        create_railway_config()
        print_railway_instructions()
    elif choice == "2":
        print("\n🎨 Render deployment instructions:")
        print("1. Go to https://render.com")
        print("2. Sign up with GitHub")
        print("3. Create 3 separate Web Services")
        print("4. Connect your GitHub repo")
        print("5. Configure each service for different agents")
        print("6. Deploy and get public URLs")
    elif choice == "3":
        print("\n🟣 Heroku deployment instructions:")
        print("1. Install Heroku CLI")
        print("2. Create 3 Heroku apps")
        print("3. Add Procfile to each")
        print("4. Deploy with git push")
    elif choice == "4":
        print("\n⚡ Preparing Vercel deployment...")
        create_vercel_config()
        print("1. Go to https://vercel.com")
        print("2. Import your GitHub repo")
        print("3. Deploy with vercel.json config")
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    print("\n🎯 Next Steps:")
    print("1. Deploy your agents to chosen platform")
    print("2. Get public URLs for each agent")
    print("3. Update Agentverse with public endpoints")
    print("4. Test agents are reachable from internet")

if __name__ == "__main__":
    main()
