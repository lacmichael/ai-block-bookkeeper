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
```

---

## JournalEntry

```ts
export interface JournalEntry {
  entry_id: string;               // UUID or monotonic per org
  business_event_id: string;      // FK to BusinessEvent
  entry_ts: string;               // Posting timestamp
  memo_hash?: string;             // HMAC of any sensitive memo

  postings: Posting[];            // Must balance to zero in base currency

  // On-chain proofs
  sui: {
    digest?: string;
    object_id?: string;
    checkpoint?: number;
    recorded: boolean;
    immutable: boolean;
  };

  // Reconciliation
  reconciliation_state: 'UNRECONCILED' | 'PARTIAL' | 'RECONCILED';
  metadata?: Record<string, any>;
}
```

---

## Posting

```ts
export interface Posting {
  line_no: number;
  account_code: number;           // Chart of accounts code
  side: 'DEBIT' | 'CREDIT';
  amount_minor: bigint;           // Integer amount (minor units)
  currency: string;

  // Optional dimensions
  department?: string;
  project_code?: string;
  cost_center?: string;
  category?: string;
  subcategory?: string;
  tax_amount_minor?: bigint;
  tax_jurisdiction?: string;
}
```

---

## PartyRef

```ts
export interface PartyRef {
  party_id: string;               // Reference to Party
  role: 'VENDOR' | 'CUSTOMER' | 'EMPLOYEE' | 'INTERNAL';
}
```

---

## Party

```ts
export interface Party {
  party_id: string;
  display_name: string;
  type: 'VENDOR' | 'CUSTOMER' | 'EMPLOYEE' | 'INTERNAL';
  legal_name?: string;
  tax_id_hash?: string;           // Store hash, not raw ID
  email?: string;
  address?: Address;
  sui_address?: string;
  metadata?: Record<string, any>;
}
```

---

## DocumentMetadata

```ts
export interface DocumentMetadata {
  document_id: string;
  filename: string;
  file_type: 'PDF' | 'CSV' | 'EXCEL' | 'IMAGE';
  file_size: number;

  storage_url: string;            // e.g., local path, S3 URL
  sha256: string;                 // Integrity hash

  upload_date: string;            // ISO date-time
  processed_by_agent?: string;
  processing_timestamp?: string;
  extraction_confidence?: number;

  onchain_hash_recorded?: boolean;
  onchain_digest?: string;
}
```

---

## AuditLog

```ts
export interface AuditLog {
  log_id: string;
  timestamp: string;
  action: 'CREATE' | 'UPDATE' | 'POST_ONCHAIN' | 'RECONCILE' | 'VERIFY' | 'DISPUTE';
  entity_type: 'BUSINESS_EVENT' | 'JOURNAL_ENTRY' | 'DOCUMENT' | 'PARTY';
  entity_id: string;
  actor_type: 'USER' | 'AI_AGENT' | 'SYSTEM';
  actor_id: string;
  request_id?: string;            // Trace across systems
  changes?: {
    field: string;
    old_value: any;
    new_value: any;
  }[];
  metadata?: Record<string, any>;
}
```