# Sui Smart Contract — Financial Audit Trail

## Module: `financial_audit`

This module defines an on-chain audit trail for recording and verifying
financial transactions. Each transaction is represented by a hashed record
that can be verified independently from off-chain data.

```move
module financial_audit {

    use sui::object::{UID};
    use sui::tx_context::{TxContext};
    use sui::table::{Table};
    use sui::event;

    /// Shared object that maintains an immutable audit trail for a company
    struct AuditTrail has key {
        id: UID,
        company_id: vector<u8>,
        transaction_records: Table<vector<u8>, TransactionHash>,
        total_transactions: u64,
        last_updated: u64,
    }

    /// Immutable record of a transaction hash
    struct TransactionHash has store, copy, drop {
        tx_id: vector<u8>,          // Off-chain UUID or source reference
        amount: u64,                // Amount in minor units
        timestamp: u64,             // Unix timestamp
        document_hash: vector<u8>,  // SHA-256 hash of source document
        category: vector<u8>,       // e.g., "Software", "Payroll"
        status: u8,                 // Enum: 0=pending, 1=verified, etc.
    }

    /// Event emitted whenever a transaction is recorded
    struct TransactionRecorded has copy, drop {
        tx_id: vector<u8>,
        amount: u64,
        timestamp: u64,
        document_hash: vector<u8>,
        category: vector<u8>,
        status: u8,
    }

    /// Entry point: record a new transaction into the audit trail
    public entry fun record_transaction(
        trail: &mut AuditTrail,
        tx_data: TransactionHash,
        ctx: &mut TxContext
    ) {
        Table::insert(&mut trail.transaction_records, tx_data.tx_id, tx_data);
        trail.total_transactions = trail.total_transactions + 1;
        trail.last_updated = TxContext::epoch(ctx);

        // Emit event for off-chain indexers
        event::emit(TransactionRecorded {
            tx_id: tx_data.tx_id,
            amount: tx_data.amount,
            timestamp: tx_data.timestamp,
            document_hash: tx_data.document_hash,
            category: tx_data.category,
            status: tx_data.status,
        });
    }

    /// Verify whether a transaction exists in the audit trail
    public fun verify_transaction(
        trail: &AuditTrail,
        tx_id: vector<u8>
    ): bool {
        Table::contains(&trail.transaction_records, &tx_id)
    }
}