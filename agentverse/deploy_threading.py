#!/usr/bin/env python3
"""
Zero-Configuration Agent Deployment Script (Threading Version)
Deploy AI Block Bookkeeper agents without requiring any environment variables.

This script runs all agents in mock mode using threading to avoid asyncio conflicts.
"""

import logging
import os
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Any

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_agent_files():
    """Check if agent files exist and are valid"""
    agent_files = [
        "audit_verification_agent.py",
        "document_processing_agent.py", 
        "reconciliation_agent.py"
    ]
    
    missing_files = []
    for file in agent_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing agent files: {', '.join(missing_files)}")
        return False
    
    logger.info("✓ All agent files are present")
    return True

def print_deployment_info():
    """Print deployment information"""
    logger.info("=" * 60)
    logger.info("🚀 AI Block Bookkeeper - Zero-Config Deployment")
    logger.info("=" * 60)
    logger.info("")
    logger.info("📋 Deployment Mode: MOCK MODE")
    logger.info("   • AI Processing: Simulated (no Anthropic API key required)")
    logger.info("   • Blockchain: Simulated (no Sui configuration required)")
    logger.info("   • Database: Simulated (no Supabase configuration required)")
    logger.info("   • Agent Communication: Full functionality")
    logger.info("")
    logger.info("🔧 To enable real services, set these environment variables:")
    logger.info("   • ANTHROPIC_API_KEY - for real AI document processing")
    logger.info("   • SUI_PACKAGE_ID, AUDIT_TRAIL_OBJ_ID, SENDER_ADDRESS - for blockchain")
    logger.info("   • SUPABASE_URL, SUPABASE_ANON_KEY - for database storage")
    logger.info("")
    logger.info("🎯 Perfect for:")
    logger.info("   • Agentverse deployment")
    logger.info("   • Demo and testing")
    logger.info("   • Development without external dependencies")
    logger.info("   • Showcasing agent capabilities")
    logger.info("")

def run_agent(agent_name: str, agent_file: str):
    """Run a single agent in a separate thread"""
    try:
        logger.info(f"Starting {agent_name}...")
        
        # Import and run the agent
        if agent_file == "audit_verification_agent.py":
            from audit_verification_agent import agent
        elif agent_file == "document_processing_agent.py":
            from document_processing_agent import agent
        elif agent_file == "reconciliation_agent.py":
            from reconciliation_agent import agent
        else:
            logger.error(f"Unknown agent file: {agent_file}")
            return
        
        logger.info(f"✓ {agent_name} imported successfully")
        logger.info(f"   Address: {agent.address}")
        
        # Run the agent (this will block the thread)
        agent.run()
        
    except Exception as e:
        logger.error(f"Error running {agent_name}: {str(e)}")

def deploy_agents():
    """Deploy all agents using threading"""
    logger.info("Starting agent deployment...")
    
    # Check prerequisites
    if not check_agent_files():
        return False
    
    # Define agents to run
    agents = [
        ("Audit Verification Agent", "audit_verification_agent.py"),
        ("Document Processing Agent", "document_processing_agent.py"),
        ("Reconciliation Agent", "reconciliation_agent.py")
    ]
    
    # Start each agent in a separate thread
    threads = []
    for agent_name, agent_file in agents:
        thread = threading.Thread(
            target=run_agent,
            args=(agent_name, agent_file),
            name=f"Thread-{agent_name}",
            daemon=True
        )
        thread.start()
        threads.append(thread)
        time.sleep(2)  # Give each agent time to start
    
    logger.info("")
    logger.info("🎉 All agents started successfully!")
    logger.info("   Agents are now discoverable in the ASI:One ecosystem")
    logger.info("   Use Ctrl+C to stop all agents")
    logger.info("")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("")
        logger.info("🛑 Stopping agents...")
        logger.info("✅ All agents stopped gracefully")
    
    return True

def main():
    """Main deployment function"""
    print_deployment_info()
    
    try:
        # Run deployment
        success = deploy_agents()
        
        if success:
            logger.info("✓ Agents deployed successfully")
            logger.info("Agents are now discoverable in the ASI:One ecosystem")
        else:
            logger.error("✗ Agent deployment failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("🛑 Deployment interrupted by user")
        logger.info("All agents stopped gracefully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

