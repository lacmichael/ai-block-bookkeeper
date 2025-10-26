#!/usr/bin/env python3
"""
Zero-Configuration Agent Deployment Script
Deploy AI Block Bookkeeper agents without requiring any environment variables.

This script runs all agents in mock mode, making them immediately deployable
to Agentverse or any other platform without configuration.
"""

import asyncio
import logging
import os
import sys
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

async def deploy_agents():
    """Deploy all agents in mock mode"""
    logger.info("Starting agent deployment...")
    
    # Check prerequisites
    if not check_agent_files():
        return False
    
    # Import and run agents
    try:
        # Import agent modules
        from audit_verification_agent import agent as audit_agent
        from document_processing_agent import agent as document_agent
        from reconciliation_agent import agent as reconciliation_agent
        
        logger.info("✓ All agents imported successfully")
        
        # Print agent addresses
        logger.info("")
        logger.info("🤖 Agent Addresses:")
        logger.info(f"   Audit Agent: {audit_agent.address}")
        logger.info(f"   Document Agent: {document_agent.address}")
        logger.info(f"   Reconciliation Agent: {reconciliation_agent.address}")
        logger.info("")
        
        logger.info("🚀 Starting agents in mock mode...")
        logger.info("   Agents will simulate all operations without external dependencies")
        logger.info("   Press Ctrl+C to stop all agents")
        logger.info("")
        
        # Start agents in separate tasks
        tasks = []
        
        # Start audit agent
        audit_task = asyncio.create_task(audit_agent.run_async())
        tasks.append(audit_task)
        logger.info(f"✓ Started Audit Agent: {audit_agent.address}")
        
        # Start document agent
        document_task = asyncio.create_task(document_agent.run_async())
        tasks.append(document_task)
        logger.info(f"✓ Started Document Agent: {document_agent.address}")
        
        # Start reconciliation agent
        reconciliation_task = asyncio.create_task(reconciliation_agent.run_async())
        tasks.append(reconciliation_task)
        logger.info(f"✓ Started Reconciliation Agent: {reconciliation_agent.address}")
        
        logger.info("")
        logger.info("🎉 All agents started successfully!")
        logger.info("   Agents are now discoverable in the ASI:One ecosystem")
        logger.info("   Use Ctrl+C to stop all agents")
        logger.info("")
        
        # Wait for all agents to run
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping agents...")
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("✅ All agents stopped gracefully")
        
    except ImportError as e:
        logger.error(f"Failed to import agents: {e}")
        return False
    except Exception as e:
        logger.error(f"Error deploying agents: {e}")
        return False
    
    return True

def main():
    """Main deployment function"""
    print_deployment_info()
    
    try:
        # Run deployment
        success = asyncio.run(deploy_agents())
        
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
