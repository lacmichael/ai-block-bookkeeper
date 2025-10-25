# Domain Models (TypeScript)

## BusinessEvent

```ts
export interface BusinessEvent {
  event_id: string;               // UUID
  source_system: 'PLAID' | 'MANUAL' | 'INVOICE_PORTAL' | 'SUI' | 'OTHER';
  source_id: string;              // e.g., Plaid transaction_id, invoice number
  occurred_at: string;            // ISO date-time
  recorded_at: string;            // When ingested
  event_kind: 'BANK_POSTED' | 'INVOICE_RECEIVED' | 'PAYMENT_SENT' | 'REFUND' | 'ADJUSTMENT';

  // Raw monetary facts
  amount_minor: bigint;           // Integer in minor units (no floats)
  currency: string;               // ISO 4217 (USD, EUR, etc.)
  description?: string;

  payer?: PartyRef;
  payee?: PartyRef;

  // Documents / attachments
  documents: DocumentMetadata[];

  // Processing state
  processing: {
    state: 'PENDING' | 'MAPPED' | 'POSTED_ONCHAIN' | 'INDEXED' | 'FAILED';
    last_error?: string;
  };

  // Idempotency
  dedupe_key: string;             // `${source_system}:${source_id}`

  metadata?: Record<string, any>;
}