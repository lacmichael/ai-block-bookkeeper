# FastAPI route for Transaction Details
# This file contains the API endpoint for fetching transaction details and Sui blockchain data
import httpx
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

router = APIRouter()

# --- Pydantic Models ---

class SuiEvent(BaseModel):
    """Model for Sui blockchain events"""
    type: str
    description: str
    timestamp: str
    data: Dict[str, Any]

class SuiTransaction(BaseModel):
    """Model for Sui blockchain transaction"""
    digest: str
    timestamp: str
    status: str
    gasUsed: int
    gasPrice: int
    sender: str
    recipient: str
    amount: int
    currency: str
    blockHeight: int
    epoch: int
    events: List[SuiEvent]

class TransactionDetailsResponse(BaseModel):
    """Response model for transaction details"""
    transaction: SuiTransaction
    auditTrail: List[Dict[str, Any]]

# --- API Endpoints ---

@router.get("/{transaction_id}", response_model=TransactionDetailsResponse)
async def get_transaction_details(transaction_id: str):
    """
    Get detailed transaction information including Sui blockchain data.
    
    Args:
        transaction_id: The unique identifier for the transaction
        
    Returns:
        TransactionDetailsResponse containing transaction and audit trail data
        
    Raises:
        HTTPException: If transaction not found or other errors occur
    """
    try:
        # Mock Sui transaction data - in a real implementation, this would query the Sui blockchain
        # For now, we'll generate realistic mock data based on the transaction ID
        
        # Generate deterministic mock data based on transaction ID
        import hashlib
        hash_obj = hashlib.md5(transaction_id.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Create mock Sui transaction
        sui_transaction = SuiTransaction(
            digest=f"0x{hash_hex[:64]}",
            timestamp="2024-01-15T10:30:00Z",
            status="success",
            gasUsed=int(hash_hex[:4], 16) % 1000 + 100,
            gasPrice=1000,
            sender=f"0x{hash_hex[8:48]}",
            recipient=f"0x{hash_hex[48:88]}",
            amount=int(hash_hex[88:96], 16) % 100000 + 1000,
            currency="USD",
            blockHeight=int(hash_hex[96:104], 16) % 1000000 + 50000000,
            epoch=int(hash_hex[104:112], 16) % 100 + 1000,
            events=[
                SuiEvent(
                    type="Transfer",
                    description="Token transfer initiated",
                    timestamp="2024-01-15T10:30:00Z",
                    data={
                        "from": f"0x{hash_hex[8:48]}",
                        "to": f"0x{hash_hex[48:88]}",
                        "amount": int(hash_hex[88:96], 16) % 100000 + 1000,
                        "currency": "USD"
                    }
                ),
                SuiEvent(
                    type="BalanceUpdate",
                    description="Account balances updated",
                    timestamp="2024-01-15T10:30:01Z",
                    data={
                        "payer_balance": int(hash_hex[96:104], 16) % 100000,
                        "payee_balance": int(hash_hex[104:112], 16) % 100000
                    }
                ),
                SuiEvent(
                    type="AuditTrail",
                    description="Transaction recorded in audit trail",
                    timestamp="2024-01-15T10:30:02Z",
                    data={
                        "event_id": transaction_id,
                        "source_system": "BANK_API",
                        "reconciliation_state": "UNRECONCILED"
                    }
                )
            ]
        )
        
        # Mock audit trail data
        audit_trail = [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "action": "Transaction Created",
                "details": f"Transaction {transaction_id} created in system",
                "actor": "System",
                "status": "completed"
            },
            {
                "timestamp": "2024-01-15T10:30:01Z",
                "action": "Sui Blockchain Record",
                "details": f"Transaction recorded on Sui blockchain with digest {sui_transaction.digest}",
                "actor": "Sui Network",
                "status": "completed"
            },
            {
                "timestamp": "2024-01-15T10:30:02Z",
                "action": "Audit Trail Updated",
                "details": "Transaction added to immutable audit trail",
                "actor": "Audit System",
                "status": "completed"
            },
            {
                "timestamp": "2024-01-15T10:30:03Z",
                "action": "Reconciliation Pending",
                "details": "Transaction marked for reconciliation",
                "actor": "Reconciliation Agent",
                "status": "pending"
            }
        ]
        
        return TransactionDetailsResponse(
            transaction=sui_transaction,
            auditTrail=audit_trail
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching transaction details: {str(e)}"
        )

@router.get("/{transaction_id}/sui-events")
async def get_sui_events(transaction_id: str):
    """
    Get Sui blockchain events for a specific transaction.
    
    Args:
        transaction_id: The unique identifier for the transaction
        
    Returns:
        List of Sui events for the transaction
    """
    try:
        # In a real implementation, this would query the Sui blockchain
        # For now, return mock data
        return {
            "transaction_id": transaction_id,
            "events": [
                {
                    "type": "Transfer",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "description": "Token transfer executed",
                    "status": "success"
                },
                {
                    "type": "BalanceUpdate",
                    "timestamp": "2024-01-15T10:30:01Z",
                    "description": "Account balances updated",
                    "status": "success"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching Sui events: {str(e)}"
        )
