# Core matching logic for reconciliation agent
# This file will contain the matching algorithms and logic
from decimal import Decimal
from typing import Optional
from domain.models import BusinessEvent, MatchResult, Discrepancy

# Load this from the agent's config
# (Hardcoded here for simplicity in this pure function)
TOLERANCE_PERCENT = 0.01  # 1%
TOLERANCE_FIXED = 500     # $5.00 in minor units

def evaluate_match(
    event: BusinessEvent,
    counterpart: Optional[BusinessEvent]
) -> MatchResult:
    """
    Compares an event with its potential counterpart based on plan's logic.
    
    Args:
        event: The event that triggered the reconciliation.
        counterpart: The potential matching event found in the DB.

    Returns:
        A MatchResult object with the outcome.
    """
    if not counterpart:
        return MatchResult(type='NO_MATCH')

    # Extract matching fields
    if event.event_kind == 'INVOICE_RECEIVED':
        invoice_num = event.metadata.get('invoice_number')
        payment_ref = counterpart.metadata.get('payment_reference')
        invoice_amount = event.amount_minor
        payment_amount = counterpart.amount_minor
        invoice_id = event.event_id
        payment_id = counterpart.event_id
    else:  # event.event_kind == 'PAYMENT_SENT'
        invoice_num = counterpart.metadata.get('invoice_number')
        payment_ref = event.metadata.get('payment_reference')
        invoice_amount = counterpart.amount_minor
        payment_amount = event.amount_minor
        invoice_id = counterpart.event_id
        payment_id = event.event_id

    # Check reference match (must be exact)
    if not invoice_num or not payment_ref or invoice_num != payment_ref:
        return MatchResult(type='NO_MATCH')

    # --- Primary Match & Partial Match Logic ---
    
    # Check amount match (with tolerance)
    amount_diff = abs(invoice_amount - payment_amount)
    
    # Use the robust tolerance rule: 1% or fixed cap, whichever is less
    tolerance_percent_calc = invoice_amount * Decimal(TOLERANCE_PERCENT)
    tolerance = min(tolerance_percent_calc, Decimal(TOLERANCE_FIXED))

    if amount_diff <= tolerance:
        return MatchResult(
            type='PRIMARY_MATCH',
            confidence=1.0,
            invoice_id=invoice_id,
            payment_id=payment_id
        )
    else:
        # It's a match on reference, but a mismatch on amount
        return MatchResult(
            type='PARTIAL_MATCH',
            confidence=0.5,
            invoice_id=invoice_id,
            payment_id=payment_id,
            discrepancy=Discrepancy(
                type='AMOUNT_MISMATCH',
                invoice_amount=invoice_amount,
                payment_amount=payment_amount,
                difference=amount_diff
            )
        )
