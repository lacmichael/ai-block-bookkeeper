import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime

# The agent logic function we are testing
from agents.reconciliation_agent import handle_reconciliation_logic

# Models for test data
from domain.models import (
    BusinessEvent,
    Processing,
    EventKind
)

# --- Test Data Fixtures ---
# (These are the same as the unit test, used to create fake data)

@pytest.fixture
def base_invoice() -> BusinessEvent:
    """A standard $1000 invoice (INV-001) that is MAPPED."""
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
    """A standard $1000 payment for INV-001 that is MAPPED."""
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

# --- Integration Tests ---

@pytest.mark.asyncio
async def test_case_1_primary_match_flow(mocker, base_invoice, matching_payment):
    """
    Tests the agent's logic for a perfect Primary Match.
    Checks that it calls 'get_event', 'find_payment', and 'update_reconciled'.
    """
    # 1. Arrange: Mock all database functions
    mock_get_event = mocker.patch(
        'agents.reconciliation_agent.db_repo.get_business_event_by_id',
        new_callable=AsyncMock,
        return_value=base_invoice
    )
    mock_find_payment = mocker.patch(
        'agents.reconciliation_agent.db_repo.find_payment_by_reference',
        new_callable=AsyncMock,
        return_value=matching_payment
    )
    mock_update_reconciled = mocker.patch(
        'agents.reconciliation_agent.db_repo.update_both_to_reconciled',
        new_callable=AsyncMock
    )
    mock_flag_review = mocker.patch(
        'agents.reconciliation_agent.db_repo.flag_both_for_review',
        new_callable=AsyncMock
    )
    mock_create_audit = mocker.patch(
        'agents.reconciliation_agent.db_repo.create_audit_log',
        new_callable=AsyncMock
    )
    
    # Create a mock DB connection (it's just passed through)
    mock_db_conn = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.logger = MagicMock()

    # 2. Act: Call the logic function, passing in the mocks
    await handle_reconciliation_logic(
        mock_ctx, mock_db_conn, base_invoice.event_id
    )
    
    # 3. Assert: Check that the correct functions were called
    mock_get_event.assert_called_once_with(mock_db_conn, base_invoice.event_id)
    mock_find_payment.assert_called_once_with(
        mock_db_conn,
        payment_reference='INV-001',
        processing_state='MAPPED',
        currency='USD'
    )
    # This is the most important check for this test case
    mock_update_reconciled.assert_called_once()
    mock_flag_review.assert_not_called()
    mock_create_audit.assert_called_once_with(
        mock_db_conn, "RECONCILE_SUCCESS", base_invoice.event_id, [], mocker.ANY
    )


@pytest.mark.asyncio
async def test_case_2_partial_match_flow(mocker, base_invoice, matching_payment):
    """
    Tests the agent's logic for a Partial Match (amount discrepancy).
    Checks that it calls 'get_event', 'find_payment', and 'flag_for_review'.
    """
    # 1. Arrange: Create a payment with a different amount
    matching_payment.amount_minor = 95000 # $950.00
    
    # Mock all database functions
    mock_get_event = mocker.patch(
        'agents.reconciliation_agent.db_repo.get_business_event_by_id',
        new_callable=AsyncMock,
        return_value=base_invoice
    )
    mock_find_payment = mocker.patch(
        'agents.reconciliation_agent.db_repo.find_payment_by_reference',
        new_callable=AsyncMock,
        return_value=matching_payment
    )
    mock_update_reconciled = mocker.patch(
        'agents.reconciliation_agent.db_repo.update_both_to_reconciled',
        new_callable=AsyncMock
    )
    mock_flag_review = mocker.patch(
        'agents.reconciliation_agent.db_repo.flag_both_for_review',
        new_callable=AsyncMock
    )
    mock_create_audit = mocker.patch(
        'agents.reconciliation_agent.db_repo.create_audit_log',
        new_callable=AsyncMock
    )
    
    mock_db_conn = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.logger = MagicMock()

    # 2. Act
    await handle_reconciliation_logic(
        mock_ctx, mock_db_conn, base_invoice.event_id
    )
    
    # 3. Assert
    mock_get_event.assert_called_once()
    mock_find_payment.assert_called_once()
    # This is the most important check for this test case
    mock_update_reconciled.assert_not_called()
    mock_flag_review.assert_called_once() # Should be flagged for review
    mock_create_audit.assert_called_once_with(
        mock_db_conn, "RECONCILE_FAIL_PARTIAL", base_invoice.event_id, [], mocker.ANY
    )


@pytest.mark.asyncio
async def test_case_3_no_match_flow(mocker, base_invoice):
    """
    Tests the agent's logic for an Orphaned Invoice (no counterpart found).
    Checks that it updates the 'reconciliation_attempted_at' timestamp.
    """
    # 1. Arrange: Program the DB to return *None* for the counterpart
    mock_get_event = mocker.patch(
        'agents.reconciliation_agent.db_repo.get_business_event_by_id',
        new_callable=AsyncMock,
        return_value=base_invoice
    )
    mock_find_payment = mocker.patch(
        'agents.reconciliation_agent.db_repo.find_payment_by_reference',
        new_callable=AsyncMock,
        return_value=None  # <--- No counterpart found
    )
    mock_update_reconciled = mocker.patch(
        'agents.reconciliation_agent.db_repo.update_both_to_reconciled',
        new_callable=AsyncMock
    )
    mock_flag_review = mocker.patch(
        'agents.reconciliation_agent.db_repo.flag_both_for_review',
        new_callable=AsyncMock
    )
    mock_update_attempt = mocker.patch(
        'agents.reconciliation_agent.db_repo.update_reconciliation_attempt',
        new_callable=AsyncMock
    )
    
    mock_db_conn = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.logger = MagicMock()

    # 2. Act
    await handle_reconciliation_logic(
        mock_ctx, mock_db_conn, base_invoice.event_id
    )
    
    # 3. Assert
    mock_get_event.assert_called_once()
    mock_find_payment.assert_called_once()
    # This is the most important check for this test case
    mock_update_attempt.assert_called_once_with(mock_db_conn, base_invoice.event_id, mocker.ANY)
    # Nothing should be updated or flagged
    mock_update_reconciled.assert_not_called()
    mock_flag_review.assert_not_called()
