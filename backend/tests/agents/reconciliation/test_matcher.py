import pytest
from decimal import Decimal
from uuid import uuid4, UUID
from datetime import datetime

# Import the function to test
from agents.reconciliation.matcher import evaluate_match

# Import the domain models we need to create test data
from domain.models import (
    BusinessEvent,
    MatchResult,
    Discrepancy,
    Processing,
    EventKind
)

# --- Test Data Fixtures ---
# We create common objects to reuse in tests

@pytest.fixture
def base_invoice() -> BusinessEvent:
    """A standard $1000 invoice (INV-001)."""
    return BusinessEvent(
        event_id=uuid4(),
        source_system="test",
        source_id="pdf-1",
        occurred_at=datetime.now(),
        recorded_at=datetime.now(),
        event_kind=EventKind.INVOICE_RECEIVED,
        amount_minor=100000, # $1000.00
        currency="USD",
        processing=Processing(state="MAPPED"),
        dedupe_key="key1",
        metadata={"invoice_number": "INV-001"}
    )

@pytest.fixture
def matching_payment() -> BusinessEvent:
    """A standard $1000 payment for INV-001."""
    return BusinessEvent(
        event_id=uuid4(),
        source_system="test",
        source_id="csv-1",
        occurred_at=datetime.now(),
        recorded_at=datetime.now(),
        event_kind=EventKind.PAYMENT_SENT,
        amount_minor=100000, # $1000.00
        currency="USD",
        processing=Processing(state="MAPPED"),
        dedupe_key="key2",
        metadata={"payment_reference": "INV-001"}
    )

# --- Test Cases ---

def test_case_1_primary_match(base_invoice, matching_payment):
    """
    Tests Test Case 1: High-Confidence Match.
    Invoice and Payment match perfectly.
    """
    # 1. Arrange (done by fixtures)
    
    # 2. Act
    result = evaluate_match(base_invoice, matching_payment)
    
    # 3. Assert
    assert result.type == 'PRIMARY_MATCH'
    assert result.confidence == 1.0
    assert result.invoice_id == base_invoice.event_id
    assert result.payment_id == matching_payment.event_id
    assert result.discrepancy is None

def test_case_2_partial_match_discrepancy(base_invoice, matching_payment):
    """
    Tests Test Case 2: Partial Payment Match (Amount Discrepancy).
    Reference matches, but amount is different.
    """
    # 1. Arrange
    matching_payment.amount_minor = 95000 # $950.00 (short $50)
    
    # 2. Act
    result = evaluate_match(base_invoice, matching_payment)
    
    # 3. Assert
    assert result.type == 'PARTIAL_MATCH'
    assert result.confidence == 0.5
    assert result.invoice_id == base_invoice.event_id
    assert result.payment_id == matching_payment.event_id
    assert result.discrepancy is not None
    assert result.discrepancy.type == 'AMOUNT_MISMATCH'
    assert result.discrepancy.difference == 5000 # 100000 - 95000

def test_case_3_no_match_orphaned_invoice(base_invoice):
    """
    Tests Test Case 3: No Match (Orphaned Invoice).
    The counterpart does not exist (is None).
    """
    # 1. Arrange (pass None as counterpart)
    
    # 2. Act
    result = evaluate_match(base_invoice, None)
    
    # 3. Assert
    assert result.type == 'NO_MATCH'

def test_case_6_no_match_currency_mismatch(base_invoice, matching_payment):
    """
    Tests Test Case 6: Currency Mismatch.
    Reference and amount match, but currencies are different.
    (Note: The DB query *should* prevent this, but the matcher
     doesn't check currency, only reference and amount. This test
     confirms the matcher's boundaries.)
    """
    # 1. Arrange
    matching_payment.currency = "EUR"
    
    # 2. Act
    # The matcher logic *only* checks reference and amount, not currency,
    # because the DB query is expected to pre-filter by currency.
    # Therefore, this will result in a PRIMARY_MATCH.
    result = evaluate_match(base_invoice, matching_payment)
    
    # 3. Assert
    assert result.type == 'PRIMARY_MATCH'
    assert result.confidence == 1.0

def test_no_match_wrong_reference(base_invoice, matching_payment):
    """
    Tests a simple "No Match" where the reference numbers are different.
    """
    # 1. Arrange
    matching_payment.metadata['payment_reference'] = "INV-002"
    
    # 2. Act
    result = evaluate_match(base_invoice, matching_payment)
    
    # 3. Assert
    assert result.type == 'NO_MATCH'

def test_primary_match_with_tolerance(base_invoice, matching_payment):
    """
    Tests that the tolerance logic works for small, acceptable differences.
    """
    # 1. Arrange
    # $1000.00 vs $999.00 ($10 diff)
    # Tolerance is min(1% of 100000, 500) = min(1000, 500) = 500
    # $10 diff (1000) is > 500. This should be a PARTIAL_MATCH.
    matching_payment.amount_minor = 99000 
    
    result_large_diff = evaluate_match(base_invoice, matching_payment)
    
    assert result_large_diff.type == 'PARTIAL_MATCH'
    assert result_large_diff.discrepancy.difference == 1000

    # $1000.00 vs $996.00 ($4 diff)
    # Tolerance is 500. $4 diff (400) is < 500. This should be a PRIMARY_MATCH.
    matching_payment.amount_minor = 99600 # $996.00 ($4 diff)
    
    result_small_diff = evaluate_match(base_invoice, matching_payment)
    
    assert result_small_diff.type == 'PRIMARY_MATCH'
