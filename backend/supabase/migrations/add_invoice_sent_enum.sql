-- Migration: Add INVOICE_SENT to event_kind enum
-- This migration adds the INVOICE_SENT value to the existing event_kind enum
-- Created by: Fix for document processing validation error

-- First, check if the enum exists and what values it has
DO $$
BEGIN
    -- Check if the enum exists
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'event_kind') THEN
        -- Add INVOICE_SENT to the enum if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'INVOICE_SENT' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'event_kind')) THEN
            ALTER TYPE event_kind ADD VALUE 'INVOICE_SENT';
            RAISE NOTICE 'Added INVOICE_SENT to event_kind enum';
        ELSE
            RAISE NOTICE 'INVOICE_SENT already exists in event_kind enum';
        END IF;
    ELSE
        -- Create the enum if it doesn't exist
        CREATE TYPE event_kind AS ENUM ('INVOICE_RECEIVED', 'INVOICE_SENT', 'PAYMENT_SENT', 'BANK_POSTED', 'REFUND', 'ADJUSTMENT');
        RAISE NOTICE 'Created event_kind enum with all values';
    END IF;
END $$;

-- Add comment for documentation
COMMENT ON TYPE event_kind IS 'Enum for business event types: INVOICE_RECEIVED, INVOICE_SENT, PAYMENT_SENT, BANK_POSTED, REFUND, ADJUSTMENT';
