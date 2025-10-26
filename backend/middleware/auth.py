"""
Authentication middleware for validating JWT tokens
"""

from typing import Optional
from fastapi import Header, HTTPException, Depends
from utils.jwt_utils import verify_jwt_token, get_wallet_address_from_token


async def get_optional_wallet_user(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Dependency that extracts wallet address from JWT if present.
    Does not require authentication (returns None if not authenticated).
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        Wallet address if authenticated, None otherwise
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    wallet_address = get_wallet_address_from_token(token)
    
    return wallet_address


async def get_required_wallet_user(authorization: Optional[str] = Header(None)) -> str:
    """
    Dependency that requires valid JWT authentication.
    Raises HTTPException if not authenticated.
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        Wallet address
        
    Raises:
        HTTPException: If not authenticated or token is invalid
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.replace("Bearer ", "")
    wallet_address = get_wallet_address_from_token(token)
    
    if not wallet_address:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return wallet_address


async def verify_token_middleware(authorization: Optional[str] = Header(None)) -> dict:
    """
    Middleware that verifies JWT token and returns the full payload.
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        JWT payload dict
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.replace("Bearer ", "")
    payload = verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload


# Convenience aliases
OptionalWalletAuth = Depends(get_optional_wallet_user)
RequiredWalletAuth = Depends(get_required_wallet_user)

