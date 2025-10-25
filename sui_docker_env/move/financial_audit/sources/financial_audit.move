module financial_audit::financial_audit {
    use sui::object::{Self, UID};
    use sui::tx_context::{TxContext};
    use sui::table::{Self, Table};
    use sui::event;
    use sui::transfer;

    /// Shared object that maintains an immutable audit trail for a company
    public struct AuditTrail has key {
        id: UID,
        company_id: vector<u8>,
        transaction_records: Table<vector<u8>, TransactionHash>,
        total_transactions: u64,
        last_updated: u64,
    }

    /// Immutable record of a transaction hash
    public struct TransactionHash has store, copy, drop {
        tx_id: vector<u8>,          // Off-chain UUID or source reference
        amount: u64,                // Amount in minor units
        timestamp: u64,             // Unix timestamp
        document_hash: address,     // SHA-256 hash of source document (32 bytes)
        category: vector<u8>,       // e.g., "Software", "Payroll"
        status: u8,                 // Enum: 0=pending, 1=verified, etc.
    }

    /// Event emitted whenever a transaction is recorded
    public struct TransactionRecorded has copy, drop {
        tx_id: vector<u8>,
        amount: u64,
        timestamp: u64,
        document_hash: address,
        category: vector<u8>,
        status: u8,
    }

    /// Initialize a new audit trail
    public entry fun init_audit_trail(
        company_id: vector<u8>,
        ctx: &mut TxContext
    ) {
        let trail = AuditTrail {
            id: object::new(ctx),
            company_id,
            transaction_records: table::new(ctx),
            total_transactions: 0,
            last_updated: 0,
        };
        transfer::share_object(trail);
    }

    /// Entry point: record a new transaction into the audit trail (accepts individual fields)
    public entry fun record_transaction_fields(
        trail: &mut AuditTrail,
        tx_id: vector<u8>,
        amount: u64,
        timestamp: u64,
        document_hash: address,
        category: vector<u8>,
        status: u8,
        ctx: &mut TxContext
    ) {
        let tx_data = TransactionHash {
            tx_id,
            amount,
            timestamp,
            document_hash,
            category,
            status,
        };
        
        table::add(&mut trail.transaction_records, tx_id, tx_data);
        trail.total_transactions = trail.total_transactions + 1;
        trail.last_updated = sui::tx_context::epoch(ctx);

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
        table::contains(&trail.transaction_records, tx_id)
    }
}
