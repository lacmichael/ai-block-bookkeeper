#!/usr/bin/env python3
"""
ASI:One Chat Protocol Test Script
Test the chat functionality of AI Block Bookkeeper agents
"""

import asyncio
import logging
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chat Protocol Models
class ChatMessage(Model):
    """ASI:One Chat Protocol message"""
    message: str
    user_id: str = "test_user"
    session_id: str = "test_session"

class ChatResponse(Model):
    """ASI:One Chat Protocol response"""
    response: str
    success: bool
    metadata: dict = {}

# Create test agent
test_agent = Agent(
    name="ChatTestAgent",
    seed="chat-test-agent-seed-12345",
    port=8005,
    endpoint=["http://127.0.0.1:8005/submit"],
)

# Fund the agent
fund_agent_if_low(test_agent.wallet.address())

async def test_chat_with_agent(agent_address: str, agent_name: str, test_messages: list):
    """Test chat functionality with a specific agent"""
    logger.info(f"\n🤖 Testing {agent_name} at {agent_address}")
    logger.info("=" * 50)
    
    for message in test_messages:
        logger.info(f"📤 Sending: {message}")
        
        try:
            # Send chat message
            chat_msg = ChatMessage(message=message)
            response = await test_agent.send_and_wait_response(
                agent_address, 
                chat_msg, 
                response_type=ChatResponse,
                timeout=10.0
            )
            
            if response:
                logger.info(f"📥 Response: {response.response}")
                if response.metadata:
                    logger.info(f"📊 Metadata: {response.metadata}")
            else:
                logger.warning("❌ No response received")
                
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
        
        logger.info("-" * 30)

async def main():
    """Main test function"""
    logger.info("🚀 ASI:One Chat Protocol Test")
    logger.info("Testing AI Block Bookkeeper agents chat functionality")
    
    # Test messages for each agent
    test_messages = [
        "hello",
        "help",
        "status",
        "capabilities",
        "what can you do?"
    ]
    
    # Agent addresses (you'll need to get these from running agents)
    agents_to_test = [
        # ("agent_address_here", "Agent Name"),
        # Add actual agent addresses when they're running
    ]
    
    if not agents_to_test:
        logger.info("⚠️ No agent addresses configured for testing")
        logger.info("To test:")
        logger.info("1. Start agents: python deploy_no_env.py")
        logger.info("2. Copy agent addresses from logs")
        logger.info("3. Update this script with actual addresses")
        return
    
    # Test each agent
    for agent_address, agent_name in agents_to_test:
        await test_chat_with_agent(agent_address, agent_name, test_messages)
    
    logger.info("\n✅ Chat protocol test completed!")

if __name__ == "__main__":
    asyncio.run(main())

