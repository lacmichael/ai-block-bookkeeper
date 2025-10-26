"""
JWT token generation and verification utilities for wallet authentication
"""

import os
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError

# Get JWT configuration from environment variables
# Use Supabase JWT Secret if available, otherwise fall back to custom secret
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
JWT_SECRET_KEY = SUPABASE_JWT_SECRET or os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))


def wallet_address_to_uuid(wallet_address: str) -> str:
    """
    Generate a deterministic UUID from a wallet address.
    Same wallet address always produces the same UUID.
    
    Args:
        wallet_address: The Sui wallet address
        
    Returns:
        UUID string
    """
    # Create a hash of the wallet address
    hash_bytes = hashlib.sha256(wallet_address.encode()).digest()
    # Use first 16 bytes to create a UUID
    return str(uuid.UUID(bytes=hash_bytes[:16]))


def create_jwt_token(wallet_address: str) -> str:
    """
    Create a JWT token for a wallet address
    
    If SUPABASE_JWT_SECRET is set, creates a Supabase-compatible JWT.
    Otherwise, creates a custom JWT.
    
    Args:
        wallet_address: The Sui wallet address
        
    Returns:
        JWT token string
    """
    now = int(time.time())
    expiration = now + (JWT_EXPIRATION_HOURS * 3600)
    
    if SUPABASE_JWT_SECRET:
        # Create Supabase-compatible JWT
        # Generate deterministic UUID from wallet address
        user_id = wallet_address_to_uuid(wallet_address)
        
        payload = {
            "aud": "authenticated",
            "exp": expiration,
            "iat": now,
            "iss": "supabase",
            "sub": user_id,  # Use UUID as user ID (required by Supabase)
            "role": "authenticated",
            "email": f"{wallet_address}@wallet.sui",  # Optional but helps identify user
            "user_metadata": {
                "wallet_address": wallet_address,
                "auth_type": "sui_wallet"
            },
            "app_metadata": {
                "provider": "sui_wallet"
            }
        }
    else:
        # Create custom JWT
        payload = {
            "sub": wallet_address,
            "iat": now,
            "exp": expiration,
            "type": "wallet_auth"
        }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def verify_jwt_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token
    
    Args:
        token: The JWT token string
        
    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # For Supabase tokens, don't check type field
        if SUPABASE_JWT_SECRET:
            return payload
        
        # For custom tokens, verify token type
        if payload.get("type") != "wallet_auth":
            return None
            
        return payload
    except InvalidTokenError:
        return None


def decode_jwt_token(token: str) -> Optional[dict]:
    """
    Decode JWT token without verification (for extracting info)
    
    Args:
        token: The JWT token string
        
    Returns:
        Decoded payload if decodable, None otherwise
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception:
        return None


def get_wallet_address_from_token(token: str) -> Optional[str]:
    """
    Extract wallet address from JWT token
    
    Args:
        token: The JWT token string
        
    Returns:
        Wallet address if valid, None otherwise
    """
    payload = verify_jwt_token(token)
    if payload:
        # For Supabase tokens, get wallet from user_metadata
        if SUPABASE_JWT_SECRET and "user_metadata" in payload:
            return payload["user_metadata"].get("wallet_address")
        # For custom tokens, get from sub field
        return payload.get("sub")
    return None

