-- Migration: Create reconciliations table
-- This table stores matched invoice-to-payment reconciliation records
-- Created by: Reconciliation Agent implementation

CREATE TABLE IF NOT EXISTS reconciliations (
    reconciliation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_event_id UUID NOT NULL,
    payment_event_id UUID NOT NULL,
    match_type VARCHAR(20) NOT NULL CHECK (match_type IN ('PRIMARY_MATCH', 'PARTIAL_MATCH')),
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    amount_difference INT DEFAULT 0,
    discrepancy JSONB,
    reconciled_at TIMESTAMPTZ DEFAULT NOW(),
    reconciled_by VARCHAR(50) DEFAULT 'reconciliation-agent',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_reconciliations_invoice ON reconciliations(invoice_event_id);
CREATE INDEX IF NOT EXISTS idx_reconciliations_payment ON reconciliations(payment_event_id);
CREATE INDEX IF NOT EXISTS idx_reconciliations_reconciled_at ON reconciliations(reconciled_at DESC);
CREATE INDEX IF NOT EXISTS idx_reconciliations_match_type ON reconciliations(match_type);

-- Add foreign key constraints if business_events table exists
-- Note: These will need to be added after business_events table is created
-- ALTER TABLE reconciliations ADD CONSTRAINT fk_reconciliations_invoice 
--     FOREIGN KEY (invoice_event_id) REFERENCES business_events(event_id) ON DELETE CASCADE;
-- ALTER TABLE reconciliations ADD CONSTRAINT fk_reconciliations_payment 
--     FOREIGN KEY (payment_event_id) REFERENCES business_events(event_id) ON DELETE CASCADE;

-- Add comment for documentation
COMMENT ON TABLE reconciliations IS 'Stores matched invoice-to-payment reconciliation records created by the Reconciliation Agent';
COMMENT ON COLUMN reconciliations.match_type IS 'Type of match: PRIMARY_MATCH (exact match within tolerance) or PARTIAL_MATCH (reference match but amount mismatch)';
COMMENT ON COLUMN reconciliations.confidence IS 'Match confidence score between 0 and 1';
COMMENT ON COLUMN reconciliations.amount_difference IS 'Absolute difference between invoice and payment amounts in minor units';
COMMENT ON COLUMN reconciliations.discrepancy IS 'JSON object containing details of any discrepancies found';

