#!/usr/bin/env python3
"""
Individual Agent Runner
Run a single agent without asyncio conflicts
"""

import sys
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run a specific agent"""
    if len(sys.argv) < 2:
        print("Usage: python run_agent.py <agent_name>")
        print("Available agents: audit, document, reconciliation")
        sys.exit(1)
    
    agent_name = sys.argv[1].lower()
    
    try:
        if agent_name == "audit":
            logger.info("Starting Audit Verification Agent...")
            from audit_verification_agent import agent
        elif agent_name == "document":
            logger.info("Starting Document Processing Agent...")
            from document_processing_agent import agent
        elif agent_name == "reconciliation":
            logger.info("Starting Reconciliation Agent...")
            from reconciliation_agent import agent
        else:
            logger.error(f"Unknown agent: {agent_name}")
            sys.exit(1)
        
        logger.info(f"Agent address: {agent.address}")
        logger.info("Agent started successfully!")
        logger.info("Press Ctrl+C to stop")
        
        # Run the agent
        agent.run()
        
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

