# Domain Models (TypeScript)

This file defines the core domain models for the Sui-based bookkeeping and finance automation MVP.  
Each model represents a logical part of the system and how it interacts with both off-chain services and the blockchain.

---

## BusinessEvent
Represents a **real-world financial event** (e.g., invoice received, bank transaction, payment, refund).  
Acts as the raw input before it’s mapped into accounting entries.

```ts
export interface BusinessEvent {
  event_id: string;               // UUID
  source_system: 'PLAID' | 'MANUAL' | 'INVOICE_PORTAL' | 'SUI' | 'OTHER';
  source_id: string;              // External identifier (Plaid txn ID, invoice #)
  occurred_at: string;            // When the event happened
  recorded_at: string;            // When the system ingested it
  event_kind: 'BANK_POSTED' | 'INVOICE_RECEIVED' | 'PAYMENT_SENT' | 'REFUND' | 'ADJUSTMENT';

  // Raw monetary facts
  amount_minor: bigint;           // Amount in minor units (integer only)
  currency: string;               // ISO 4217 (USD, EUR, etc.)
  description?: string;

  payer?: PartyRef;               // Optional payer reference
  payee?: PartyRef;               // Optional payee reference

  // Linked documents or attachments
  documents: DocumentMetadata[];

  // Processing and ingestion state
  processing: {
    state: 'PENDING' | 'MAPPED' | 'POSTED_ONCHAIN' | 'INDEXED' | 'FAILED';
    last_error?: string;
  };

  // Ensures duplicates aren’t created if re-ingested
  dedupe_key: string;             // `${source_system}:${source_id}`

  metadata?: Record<string, any>; // Free-form extension fields
}
```

---

## JournalEntry
Represents a **balanced accounting entry** derived from a BusinessEvent.  
Contains one or more postings (debits and credits) and serves as the system’s immutable ledger entry.

```ts
export interface JournalEntry {
  entry_id: string;               // UUID or monotonic per org
  business_event_id: string;      // Links back to the originating event
  entry_ts: string;               // When the entry was created
  memo_hash?: string;             // HMAC of any sensitive memo text

  postings: Posting[];            // Balanced DR/CR lines

  // On-chain verification data
  sui: {
    digest?: string;              // Sui tx digest
    object_id?: string;           // Related on-chain object
    checkpoint?: number;
    recorded: boolean;            // Whether it’s written on-chain
    immutable: boolean;           // True once finalized
  };

  // Reconciliation state (used for matching to invoices/payments)
  reconciliation_state: 'UNRECONCILED' | 'PARTIAL' | 'RECONCILED';

  metadata?: Record<string, any>;
}
```

---

## Posting
Represents a **single debit or credit line** inside a JournalEntry.  
Used to track specific accounts and categories.

```ts
export interface Posting {
  line_no: number;                // Sequential line number
  account_code: number;           // Chart of accounts code
  side: 'DEBIT' | 'CREDIT';       // Accounting side
  amount_minor: bigint;           // Amount in minor units
  currency: string;               // Currency for this posting

  // Optional analytical dimensions
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
Lightweight pointer linking a BusinessEvent or Posting to a Party.

```ts
export interface PartyRef {
  party_id: string;               // Reference to Party entity
  role: 'VENDOR' | 'CUSTOMER' | 'EMPLOYEE' | 'INTERNAL';
}
```

---

## Party
Represents a **person or organization** involved in financial transactions  
(vendors, customers, employees, or internal departments).

```ts
export interface Party {
  party_id: string;
  display_name: string;
  type: 'VENDOR' | 'CUSTOMER' | 'EMPLOYEE' | 'INTERNAL';
  legal_name?: string;
  tax_id_hash?: string;           // Store hash instead of raw tax ID for privacy
  email?: string;
  address?: Address;
  sui_address?: string;           // Optional blockchain identity
  metadata?: Record<string, any>;
}
```

---

## DocumentMetadata
Represents any **file or artifact** linked to financial events  
(invoices, receipts, statements, CSV exports, etc.) and ensures file integrity.

```ts
export interface DocumentMetadata {
  document_id: string;
  filename: string;
  file_type: 'PDF' | 'CSV' | 'EXCEL' | 'IMAGE';
  file_size: number;

  storage_url: string;            // e.g., local path, S3 bucket URL
  sha256: string;                 // Integrity hash for verification

  upload_date: string;            // ISO date-time
  processed_by_agent?: string;    // Which Fetch agent parsed it
  processing_timestamp?: string;
  extraction_confidence?: number; // 0–1 confidence score from AI extraction

  onchain_hash_recorded?: boolean;
  onchain_digest?: string;        // Related blockchain transaction
}
```

---

## AuditLog
Captures **who did what and when** for full traceability.  
Every mutation to a BusinessEvent, JournalEntry, Document, or Party should emit an AuditLog entry.

```ts
export interface AuditLog {
  log_id: string;
  timestamp: string;
  action: 'CREATE' | 'UPDATE' | 'POST_ONCHAIN' | 'RECONCILE' | 'VERIFY' | 'DISPUTE';
  entity_type: 'BUSINESS_EVENT' | 'JOURNAL_ENTRY' | 'DOCUMENT' | 'PARTY';
  entity_id: string;
  actor_type: 'USER' | 'AI_AGENT' | 'SYSTEM';
  actor_id: string;
  request_id?: string;            // Correlates multi-step actions
  changes?: {
    field: string;
    old_value: any;
    new_value: any;
  }[];
  metadata?: Record<string, any>;
}
```