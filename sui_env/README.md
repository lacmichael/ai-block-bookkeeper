# Sui Local Network - GraphQL + General-Purpose Indexer Stack

A production-ready Dockerized Sui local network following the [official Sui data serving architecture](https://docs.sui.io/guides/developer/sui-101/data-serving).

## Features

- **Fast Startup**: Network ready in ~30 seconds
- **Fresh Genesis on Each Start**: Network starts from scratch with `--force-regenesis` for consistent testing
- **Auto-Deploy**: Automatically publishes and initializes the `financial_audit` Move contracts
- **Official Stack**: Full node + Faucet + General-purpose Indexer + GraphQL RPC (Beta)
- **GraphQL RPC**: Modern GraphQL interface for querying blockchain data (Beta release)
- **General-Purpose Indexer**: Performant checkpoint-based indexing backed by PostgreSQL
- **Future-Ready**: gRPC port exposed for migration from deprecated JSON-RPC
- **Production Config**: Optimized connection pools, query limits, and performance tuning

## Quick Start

```bash
cd sui_env
./start.sh
```

The script will:
1. Build Docker images
2. Launch full Sui stack (node + faucet + indexer + GraphQL)
3. Publish the financial_audit Move package
4. Create initial `.sui-config` file

Then initialize the AuditTrail:
```bash
./init_audit_trail.sh
```

## Service Endpoints

| Service | Port | URL | Status |
|---------|------|-----|--------|
| JSON-RPC | 9000 | http://localhost:9000 | Deprecated (use GraphQL) |
| gRPC | 9184 | http://localhost:9184 | Future-ready |
| Faucet | 9123 | http://localhost:9123 | Active |
| GraphQL RPC | 8000 | http://localhost:8000/graphql | Beta (recommended) |
| PostgreSQL | 5432 | postgresql://sui:sui@localhost:5432/sui_indexer | Active |
| pgAdmin (GUI) | 5050 | http://localhost:5050 | Active |

## Usage

### Start the Network

```bash
./start.sh
```

After starting, initialize the AuditTrail:
```bash
./init_audit_trail.sh
```

This creates the shared AuditTrail object and updates `.sui-config`.

### View Logs

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f sui-localnet
docker compose logs -f sui-graphql
docker compose logs -f sui-indexer
```

### Stop the Network

```bash
docker compose down
```

### Reset Network (Fresh Start)

```bash
docker compose down -v
./start.sh
```

### Get Test SUI

The faucet is automatically available. To request test SUI for an address:

```bash
curl -X POST http://localhost:9123/gas \
  -H 'Content-Type: application/json' \
  -d '{"FixedAmountRequest": {"recipient": "0xYOUR_ADDRESS"}}'
```

### Initialize AuditTrail

After starting the network, initialize the AuditTrail object:

```bash
./init_audit_trail.sh
```

This will create the shared AuditTrail object and save its ID to `.sui-config`.

### Get Configuration

Easily retrieve the Package ID and AuditTrail ID:

```bash
# Show all configuration
./get_config.sh

# Get just the package ID
./get_config.sh package

# Get just the audit trail ID
./get_config.sh trail

# Load into current shell
source .sui-config

# Export to .env format
./get_config.sh env >> ../.env
```

### Query with GraphQL RPC (Recommended)

Use the built-in query script for easy GraphQL access:

```bash
# Get chain info and configuration
./query.sh gql-chain

# Query recent transactions
./query.sh gql-txs

# Query events for your package
./query.sh gql-events 0xYOUR_PACKAGE_ID

# Get objects owned by an address
./query.sh gql-objects 0xYOUR_ADDRESS

# Get balance and coins for an address
./query.sh gql-balance 0xYOUR_ADDRESS

# Custom GraphQL query
./query.sh gql '{
  transactionBlocks(first: 10) {
    nodes {
      digest
      sender { address }
      effects { status }
    }
    pageInfo { hasNextPage endCursor }
  }
}'
```

Or use curl directly for custom queries:

```bash
# Simple query
curl -X POST http://localhost:8000/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query": "{chainIdentifier}"}'

# Complex query with filtering and pagination
curl -X POST http://localhost:8000/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query": "{ events(first: 20, filter: {sender: \"0x123\"}) { nodes { timestamp sendingModule { name } } pageInfo { hasNextPage } } }"}'
```

**GraphQL Benefits:**
- Combine data from multiple tables in a single request
- Type-safe queries with autocomplete support
- Built-in pagination with `pageInfo`
- Consistent data across tables from same checkpoint
- Optimized connection pooling for better performance

### Explore Database with pgAdmin (GUI)

pgAdmin provides a visual interface to explore the indexed database:

1. **Open pgAdmin**: http://localhost:5050
2. **Login** (if prompted):
   - Email: `admin@admin.com`
   - Password: `admin`
3. **Add Server** (first time only):
   - Right-click "Servers" → "Register" → "Server"
   - **General tab**: Name = `Sui Indexer`
   - **Connection tab**:
     - Host: `postgres`
     - Port: `5432`
     - Database: `sui_indexer`
     - Username: `sui`
     - Password: `sui`
   - Click "Save"
4. **Browse tables**: Servers → Sui Indexer → Databases → sui_indexer → Schemas → public → Tables

**Useful tables to explore:**
- `transactions` - All transaction blocks
- `events` - Event emissions from contracts
- `objects` - Object states
- `checkpoints` - Network checkpoints
- `tx_calls` - Transaction function calls
- `tx_senders` - Transaction senders
- `packages` - Published Move packages

**Quick queries:**
- Right-click a table → "View/Edit Data" → "All Rows"
- Or use the Query Tool (Tools → Query Tool) for custom SQL

### Interact via Sui CLI

You can use the sui-cli container to interact with the network:

```bash
docker compose run --rm sui-cli bash

# Inside the container:
sui client new-env --alias local --rpc http://sui-localnet:9000
sui client switch --env local
sui client faucet --url http://sui-localnet:9123/gas
sui client objects
```

## Architecture

Based on the [official Sui data serving architecture](https://docs.sui.io/guides/developer/sui-101/data-serving):

```
┌──────────────────────────────────────────────────────┐
│   Sui Full Node (sui-localnet)                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  JSON-RPC (9000) - Deprecated                  │ │
│  │  gRPC API (9184) - Future migration path       │ │
│  │  Faucet (9123)                                 │ │
│  │  Checkpoint Writer (/root/.sui/checkpoints)   │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
           │
           │ Checkpoint Files (Shared Volume)
           │
           ▼
┌──────────────────────────────────────────────────────┐
│  General-Purpose Indexer (sui-indexer)              │
│  ┌────────────────────────────────────────────────┐ │
│  │  • Reads checkpoints from shared volume       │ │
│  │  • Declarative, parallel data ingestion       │ │
│  │  • Performant & scalable implementation       │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
           │
           │ Writes indexed data
           │
           ▼
┌──────────────────────────────────────────────────────┐
│  PostgreSQL Database (postgres:15)                   │
│  • Relational storage for all blockchain data        │
│  • Performance-tuned for indexer workload            │
│  • Connection pooling optimized (100 connections)    │
└──────────────────────────────────────────────────────┘
           │
           │ Read queries
           │
           ▼
┌──────────────────────────────────────────────────────┐
│  GraphQL RPC Service (sui-graphql-rpc) - Beta       │
│  ┌────────────────────────────────────────────────┐ │
│  │  • Expressive GraphQL querying (port 8000)    │ │
│  │  • Combines data from multiple tables         │ │
│  │  • Optimized connection pooling (30 conns)    │ │
│  │  • Connects to full node for live data        │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
           │
           ▼
    Your Application
```

### Key Components

- **Full Node**: Sui validator node with checkpoint ingestion enabled
- **General-Purpose Indexer**: Checkpoint-based indexer (Beta) - replaces legacy RPC polling
- **PostgreSQL**: Relational database with performance tuning
- **GraphQL RPC**: Modern query interface (Beta) - migration path from deprecated JSON-RPC

## Move Contracts

The `financial_audit` Move package is located in `move/financial_audit/` and is automatically:
1. Built during network startup
2. Published to the network
3. Initialized with an AuditTrail object

Package contents:
- `sources/financial_audit.move`: Main contract with AuditTrail and BusinessEvent structs

## Troubleshooting

### Network Not Starting

If the network fails to start:
```bash
# View detailed logs
docker compose logs sui-localnet

# Reset everything
docker compose down -v
./start.sh
```

### Port Already in Use

If ports 9000, 9123, 8000, or 5432 are already in use, you can modify them in `docker-compose.yml`:

```yaml
ports:
  - "9001:9000"  # Change external port
```

### GraphQL Service Not Responding

The GraphQL service needs time to index initial transactions. Check indexer status:

```bash
docker compose logs -f sui-indexer
docker compose logs -f sui-graphql
```

## Data Access Interfaces

This setup follows the [official Sui data serving stack](https://docs.sui.io/guides/developer/sui-101/data-serving):

### Primary Interface: GraphQL RPC (Beta)
- **Port**: 8000
- **Endpoint**: http://localhost:8000/graphql
- **Status**: Beta release - recommended for new applications
- **Benefits**: 
  - Expressive querying system
  - Combine data from multiple tables
  - Type-safe queries
  - Ideal for webapp/frontend development

### Legacy Interface: JSON-RPC
- **Port**: 9000
- **Status**: **Deprecated** - migrate to GraphQL or gRPC
- **Migration Timeline**: JSON-RPC will be deactivated by April 2026
- **Use Case**: Only for backward compatibility

### Future Interface: gRPC API
- **Port**: 9184 (exposed but not primary in local dev)
- **Status**: Generally available
- **Use Case**: Ultra low-latency applications, exchanges, DeFi protocols

## Development Tips

1. **Use GraphQL**: GraphQL RPC is the recommended interface for querying blockchain data
2. **Always start fresh**: The `--force-regenesis` flag ensures consistent state for testing
3. **Monitor logs**: Use `docker compose logs -f` to watch real-time activity
4. **Fast iteration**: Network starts in ~30 seconds, perfect for rapid testing
5. **Checkpoint-based indexing**: Indexer reads from checkpoint files for optimal performance
6. **Auto-sync**: Database automatically resets and syncs with the blockchain on restart
7. **PostgreSQL access**: Direct DB access available at `postgresql://sui:sui@localhost:5432/sui_indexer`
8. **Connection pooling**: Optimized database connection pool (30 connections) for GraphQL queries
9. **Persistent development**: If you need to persist state between runs, remove `--force-regenesis` flag and modify init process

## Query Script

The `query.sh` script provides convenient access to GraphQL RPC (recommended) and legacy JSON-RPC:

```bash
# GraphQL RPC Queries (Recommended)
./query.sh gql-chain                # Chain info and service configuration
./query.sh gql-txs                  # Recent transactions with pagination
./query.sh gql-events <PACKAGE_ID>  # Events from your package
./query.sh gql-objects <ADDRESS>    # Objects owned by address
./query.sh gql-package <PACKAGE_ID> # Package info and modules
./query.sh gql-balance <ADDRESS>    # Address balance and coins
./query.sh gql '<QUERY>'            # Custom GraphQL query

# Legacy JSON-RPC Queries (Deprecated)
./query.sh total                    # Total transactions
./query.sh events <PACKAGE_ID>      # Events from package
./query.sh tx <DIGEST>              # Transaction details
./query.sh object <OBJECT_ID>       # Object details
./query.sh audit-trail <ID>         # AuditTrail object
```

## References

### Official Sui Documentation
- [Access Sui Data - Overview](https://docs.sui.io/guides/developer/sui-101/data-serving) - Primary reference for this setup
- [GraphQL RPC (Beta)](https://docs.sui.io/guides/developer/advanced/graphql-rpc) - GraphQL RPC documentation
- [General-Purpose Indexer (Beta)](https://docs.sui.io/guides/developer/advanced/general-purpose-indexer) - Indexer setup and configuration
- [Sui Full Node gRPC](https://docs.sui.io/references/sui-full-node-grpc) - gRPC API reference
- [Sui Local Network](https://docs.sui.io/guides/developer/sui-101/local-network) - Local network setup guide

### Architecture Resources
- [When to use gRPC vs GraphQL](https://docs.sui.io/guides/developer/sui-101/data-serving#when-to-use-grpc-vs-graphql-with-general-purpose-indexer) - Decision guide
- [Custom Indexing Framework](https://docs.sui.io/guides/developer/advanced/custom-indexer) - For advanced use cases
- [Sui GitHub Repository](https://github.com/MystenLabs/sui) - Source code and examples

docker compose exec postgres psql -U sui -d sui_indexer -c "
SELECT event_type, sender, timestamp_ms 
FROM events 
ORDER BY timestamp_ms DESC 
LIMIT 10;"
