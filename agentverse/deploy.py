#!/usr/bin/env python3
"""
Agentverse Deployment Script
Deploy AI Block Bookkeeper agents to Agentverse platform
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        "ANTHROPIC_API_KEY",
        "SUI_PACKAGE_ID", 
        "AUDIT_TRAIL_OBJ_ID",
        "SENDER_ADDRESS"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file or environment")
        return False
    
    logger.info("✓ All required environment variables are set")
    return True

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

async def deploy_agents():
    """Deploy all agents to Agentverse"""
    logger.info("Starting agent deployment to Agentverse...")
    
    # Check prerequisites
    if not check_environment():
        return False
    
    if not check_agent_files():
        return False
    
    # Import and run agents
    try:
        # Import agent modules
        from audit_verification_agent import agent as audit_agent
        from document_processing_agent import agent as document_agent
        from reconciliation_agent import agent as reconciliation_agent
        
        logger.info("✓ All agents imported successfully")
        
        # Start agents concurrently
        tasks = [
            audit_agent.run(),
            document_agent.run(), 
            reconciliation_agent.run()
        ]
        
        logger.info("Starting agents...")
        logger.info(f"Audit Agent: {audit_agent.address}")
        logger.info(f"Document Agent: {document_agent.address}")
        logger.info(f"Reconciliation Agent: {reconciliation_agent.address}")
        
        # Run all agents concurrently
        await asyncio.gather(*tasks)
        
    except ImportError as e:
        logger.error(f"Failed to import agents: {e}")
        return False
    except Exception as e:
        logger.error(f"Error deploying agents: {e}")
        return False
    
    return True

def main():
    """Main deployment function"""
    logger.info("AI Block Bookkeeper - Agentverse Deployment")
    logger.info("=" * 50)
    
    try:
        # Run deployment
        success = asyncio.run(deploy_agents())
        
        if success:
            logger.info("✓ Agents deployed successfully to Agentverse")
            logger.info("Agents are now discoverable in the ASI:One ecosystem")
        else:
            logger.error("✗ Agent deployment failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

