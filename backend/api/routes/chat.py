# FastAPI route for Financial Analysis Agent chat
# This file contains the API endpoint for chat interactions with the Financial Analysis Agent
import httpx
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Get the agent's address from environment variable
FINANCIAL_AGENT_ADDRESS = os.environ.get("FINANCIAL_AGENT_ADDRESS")

if not FINANCIAL_AGENT_ADDRESS:
    raise ValueError("FINANCIAL_AGENT_ADDRESS environment variable not set")

# --- Pydantic Models ---

class ChatRequest(BaseModel):
    """Request model for chat messages"""
    message: str

class ChatResponse(BaseModel):
    """Response model for chat responses"""
    response: str

# --- API Endpoints ---

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Chat endpoint that forwards user messages to the Financial Analysis Agent.
    
    Args:
        request: ChatRequest containing the user's message
        
    Returns:
        ChatResponse containing the agent's response
        
    Raises:
        HTTPException: If communication with agent fails
    """
    try:
        # Prepare the message for the agent
        message = {"message": request.message}
        
        # Forward the message to the Financial Analysis Agent
        async with httpx.AsyncClient() as client:
            response = await client.post(
                FINANCIAL_AGENT_ADDRESS,
                json=message,
                timeout=30.0  # 30 second timeout for agent response
            )
        
        # Check if agent responded successfully
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Financial Analysis Agent returned status {response.status_code}"
            )
        
        # Extract the response from the agent
        agent_response = response.json()
        
        # Return the agent's response
        return ChatResponse(response=agent_response.get("response", "No response from agent"))
        
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Financial Analysis Agent did not respond within timeout period"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to communicate with Financial Analysis Agent: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
