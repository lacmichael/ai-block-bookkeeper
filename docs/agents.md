# AI Block Bookkeeper - Core Agents

## Overview

The AI Block Bookkeeper system is powered by 4 core agents that work together to automate financial data processing, verification, and analysis.

## Core Agents

### 1. Document Processing Agent

**Purpose:** Converts uploaded invoices and receipts (CSV, PDF) into clean, standardized transaction data.

**Key Function:** Extracts financial data from PDFs and spreadsheets, normalizes formats, and flags unclear data for human review.

---

### 2. Audit & Verification Agent

**Purpose:** Ensures data integrity by recording verified transactions to Sui blockchain.

**Key Function:** Verifies transaction authenticity, detects duplicates, and creates immutable audit trails on-chain.

---

### 3. Reconciliation Agent

**Purpose:** Automatically matches invoices to payments and identifies discrepancies.

**Key Function:** Connects related transactions (e.g., invoice + payment), updates payment statuses, and flags mismatches for review.

---

### 4. Financial Analysis Agent

**Purpose:** Provides intelligent financial insights through natural language queries.

**Key Function:** Analyzes transaction data from database and blockchain, answers questions like "What were our top expenses last month?" or "Show me all unpaid Microsoft invoices."

## System Workflow

The agents work together in the following workflow:

1. **Document Upload** - User uploads invoice/payment document (PDF/CSV)
2. **Data Extraction** - Document Processing Agent extracts transaction data using Claude
3. **Data Normalization** - Agent normalizes to BusinessEvent data model
4. **Blockchain Posting** - Audit Agent posts transaction to Sui blockchain
5. **Database Storage** - Store in Supabase with POSTED_ONCHAIN status
6. **Automatic Reconciliation** - Reconciliation Agent matches invoices to payments
7. **Status Updates** - Update transaction statuses (RECONCILED, FLAGGED_FOR_REVIEW)
8. **Financial Analysis** - Analysis Agent provides insights on reconciled data

## Agent Communication Flow

```
User Upload → Document Processing Agent
                ↓ (AuditVerificationRequest)
              Audit Agent
                ↓ (AuditVerificationResponse)
              Document Processing Agent
                ↓ (ReconciliationRequest)
              Reconciliation Agent
                ↓ (ReconciliationResponse)
              Document Processing Agent → User
```

## Agent Integration

Each agent is designed to work independently while sharing data through the central database and blockchain infrastructure, ensuring a seamless and automated financial processing pipeline. Agents communicate using the Fetch.ai uAgents framework with typed message models for reliable inter-agent communication.
