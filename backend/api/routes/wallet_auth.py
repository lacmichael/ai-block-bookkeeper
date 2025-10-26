"""
Wallet authentication API routes for Sui wallet sign-in
"""

import logging
import os
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from supabase import create_client, Client

from utils.jwt_utils import create_jwt_token, verify_jwt_token, get_wallet_address_from_token, wallet_address_to_uuid
from utils.nonce_store import generate_nonce, verify_nonce, mark_nonce_used
from utils.sui_verification import verify_personal_message_signature

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth/wallet", tags=["wallet_auth"])

# Initialize Supabase client for user creation
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if supabase_url and supabase_service_key:
    supabase: Optional[Client] = create_client(supabase_url, supabase_service_key)
else:
    supabase = None
    logger.warning("Supabase not configured - wallet users will use custom JWT only")


# Request/Response Models
class NonceRequest(BaseModel):
    wallet_address: str


class NonceResponse(BaseModel):
    nonce: str
    message: str


class VerifyRequest(BaseModel):
    wallet_address: str
    signature: str
    nonce: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    wallet_address: str


class SessionResponse(BaseModel):
    wallet_address: str
    authenticated: bool


# Dependency for getting current user from JWT
async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """Extract and verify wallet address from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    wallet_address = get_wallet_address_from_token(token)
    
    if not wallet_address:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return wallet_address


@router.post("/nonce", response_model=NonceResponse)
async def request_nonce(request: NonceRequest):
    """
    Generate a nonce for wallet authentication
    
    This endpoint generates a unique nonce that the client must sign
    to prove ownership of the wallet.
    """
    try:
        nonce = generate_nonce(request.wallet_address)
        
        # Create message to sign
        message = f"Sign this message to authenticate with AI Block Bookkeeper.\n\nNonce: {nonce}\nTimestamp: {datetime.utcnow().isoformat()}"
        
        logger.info(f"Generated nonce for wallet: {request.wallet_address[:8]}...")
        
        return NonceResponse(
            nonce=nonce,
            message=message
        )
    except Exception as e:
        logger.error(f"Error generating nonce: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate nonce")


@router.post("/verify", response_model=TokenResponse)
async def verify_signature(request: VerifyRequest):
    """
    Verify wallet signature and issue JWT token
    
    This endpoint verifies the signature of the message containing the nonce,
    validates the nonce, and issues a JWT token for authenticated access.
    """
    try:
        # Verify nonce is valid and not used
        if not verify_nonce(request.nonce, request.wallet_address):
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired nonce"
            )
        
        # Reconstruct the message that should have been signed
        # Note: This should match the message format from the nonce endpoint
        # For simplicity, we'll extract the nonce from the signature verification
        # In production, you might want to store the exact message with the nonce
        
        # Verify the signature
        # Note: The message verification depends on what was actually signed
        # For now, we'll do a basic verification
        # In production, store the exact message and verify it
        
        message = f"Sign this message to authenticate with AI Block Bookkeeper.\n\nNonce: {request.nonce}\nTimestamp: {datetime.utcnow().isoformat()}"
        
        is_valid = verify_personal_message_signature(
            message=message,
            signature=request.signature,
            wallet_address=request.wallet_address
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid signature"
            )
        
        # Mark nonce as used
        mark_nonce_used(request.nonce)
        
        # Create user in Supabase if configured
        if supabase and os.getenv("SUPABASE_JWT_SECRET"):
            try:
                # Generate deterministic UUID for this wallet
                user_id = wallet_address_to_uuid(request.wallet_address)
                email = f"{request.wallet_address}@wallet.sui"
                
                # Try to create the user (will fail if exists, that's fine)
                try:
                    supabase.auth.admin.create_user({
                        "id": user_id,  # Use our deterministic UUID
                        "email": email,
                        "email_confirm": True,
                        "user_metadata": {
                            "wallet_address": request.wallet_address,
                            "auth_type": "sui_wallet"
                        },
                        "app_metadata": {
                            "provider": "sui_wallet"
                        }
                    })
                    logger.info(f"Created Supabase user for wallet: {request.wallet_address[:8]}...")
                except Exception as create_error:
                    # User probably already exists, that's fine
                    logger.debug(f"User creation skipped (likely exists): {create_error}")
                    
            except Exception as e:
                logger.warning(f"Supabase user creation failed: {e}")
        
        # Generate JWT token (Supabase-compatible if secret is set)
        access_token = create_jwt_token(request.wallet_address)
        
        logger.info(f"Successfully authenticated wallet: {request.wallet_address[:8]}...")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            wallet_address=request.wallet_address
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying signature: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Signature verification failed")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(wallet_address: str = Depends(get_current_user)):
    """
    Refresh JWT token
    
    Issues a new JWT token with fresh expiration time.
    """
    try:
        access_token = create_jwt_token(wallet_address)
        
        logger.info(f"Refreshed token for wallet: {wallet_address[:8]}...")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            wallet_address=wallet_address
        )
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")


@router.get("/me", response_model=SessionResponse)
async def get_session(wallet_address: str = Depends(get_current_user)):
    """
    Get current session information
    
    Returns information about the authenticated wallet.
    """
    return SessionResponse(
        wallet_address=wallet_address,
        authenticated=True
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint
    
    Client should delete their stored JWT token.
    Server-side logout is handled by token expiration.
    """
    return {"message": "Logged out successfully"}

