"""
In-memory nonce storage for wallet authentication
"""

import secrets
import time
from typing import Dict, Optional

# Store format: {nonce: {"wallet_address": str, "timestamp": float, "used": bool}}
_nonce_store: Dict[str, dict] = {}

# Nonce expiration time (5 minutes)
NONCE_EXPIRATION_SECONDS = 300


def generate_nonce(wallet_address: str) -> str:
    """
    Generate a new nonce for a wallet address
    
    Args:
        wallet_address: The wallet address requesting authentication
        
    Returns:
        A random nonce string
    """
    nonce = secrets.token_urlsafe(32)
    
    _nonce_store[nonce] = {
        "wallet_address": wallet_address,
        "timestamp": time.time(),
        "used": False
    }
    
    # Clean up old nonces
    cleanup_expired_nonces()
    
    return nonce


def verify_nonce(nonce: str, wallet_address: str) -> bool:
    """
    Verify that a nonce is valid and unused
    
    Args:
        nonce: The nonce to verify
        wallet_address: The wallet address attempting to use the nonce
        
    Returns:
        True if valid and unused, False otherwise
    """
    nonce_data = _nonce_store.get(nonce)
    
    if not nonce_data:
        return False
    
    # Check if already used
    if nonce_data["used"]:
        return False
    
    # Check if expired
    if time.time() - nonce_data["timestamp"] > NONCE_EXPIRATION_SECONDS:
        del _nonce_store[nonce]
        return False
    
    # Check if wallet address matches
    if nonce_data["wallet_address"] != wallet_address:
        return False
    
    return True


def mark_nonce_used(nonce: str) -> None:
    """
    Mark a nonce as used (prevents replay attacks)
    
    Args:
        nonce: The nonce to mark as used
    """
    if nonce in _nonce_store:
        _nonce_store[nonce]["used"] = True


def cleanup_expired_nonces() -> None:
    """
    Remove expired nonces from the store
    """
    current_time = time.time()
    expired_nonces = [
        nonce for nonce, data in _nonce_store.items()
        if current_time - data["timestamp"] > NONCE_EXPIRATION_SECONDS
    ]
    
    for nonce in expired_nonces:
        del _nonce_store[nonce]


def get_nonce_info(nonce: str) -> Optional[dict]:
    """
    Get information about a nonce (for debugging)
    
    Args:
        nonce: The nonce to query
        
    Returns:
        Nonce data if exists, None otherwise
    """
    return _nonce_store.get(nonce)

