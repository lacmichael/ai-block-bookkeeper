# AI Block Bookkeeper - Core Agents

## Overview

The AI Block Bookkeeper system is powered by 4 core agents that work together to automate financial data processing, verification, and analysis.

## Core Agents

### 1. Document Processing Agent

**Purpose:** Converts uploaded invoices/CSVs into clean, standardized transaction data.

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

1. **Document Upload** - User uploads invoice (PDF/CSV)
2. **Data Extraction** - Fetch agent extracts transactions
3. **Data Normalization** - Agent normalizes to data model
4. **Database Storage** - Store in DB with PENDING status
5. **Human Review** - User reviews/verifies in frontend
6. **Blockchain Queue** - Once verified, queue for blockchain recording
7. **Batch Recording** - Batch record to Sui (daily/weekly)
8. **Reference Update** - Update DB with blockchain references
9. **Audit Trail** - Generate immutable audit trail

## Agent Integration

Each agent is designed to work independently while sharing data through the central database and blockchain infrastructure, ensuring a seamless and automated financial processing pipeline.
