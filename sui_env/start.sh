#!/usr/bin/env bash
# start.sh - Start Sui local network with full stack (indexer + GraphQL)
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================================="
echo "  Sui Local Network - GraphQL + General-Purpose Indexer"
echo "=========================================================="
echo ""

echo ">>> [1/4] Building Docker images..."
docker compose build

echo ""
echo ">>> [2/4] Starting official Sui data serving stack..."
echo "    - PostgreSQL Database (performance-tuned)"
echo "    - Full Node with checkpoint ingestion"
echo "    - Faucet Service"
echo "    - General-Purpose Indexer (checkpoint-based)"
echo "    - GraphQL RPC Service (Beta)"
docker compose up -d

echo ">>> Waiting for sui-localnet to be healthy..."
for i in $(seq 1 60); do
  status=$(docker compose ps -q sui-localnet | xargs docker inspect --format='{{json .State.Health.Status}}' 2>/dev/null || echo '"starting"')
  if [[ "$status" == "\"healthy\"" ]]; then
    echo ">>> sui-localnet is healthy"
    break
  fi
  sleep 2
  if [[ $i -eq 60 ]]; then
    echo "ERROR: sui-localnet did not become healthy in time."
    docker compose logs sui-localnet | tail -n 100
    exit 1
  fi
done

echo ">>> Waiting for GraphQL service to be healthy..."
for i in $(seq 1 60); do
  status=$(docker compose ps -q sui-graphql | xargs docker inspect --format='{{json .State.Health.Status}}' 2>/dev/null || echo '"starting"')
  if [[ "$status" == "\"healthy\"" ]]; then
    echo ">>> sui-graphql is healthy"
    break
  fi
  sleep 2
  if [[ $i -eq 60 ]]; then
    echo "⚠ WARNING: GraphQL service did not become healthy (may still be indexing)"
    break
  fi
done

echo ""
echo ">>> [3/4] Verifying services..."
echo -n "    - JSON-RPC (port 9000): "
if curl -s -X POST http://localhost:9000 \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"sui_getTotalTransactionBlocks","params":[]}' >/dev/null; then
  echo "✓"
else
  echo "✗ (RPC not responding)"
  exit 1
fi

echo -n "    - Faucet (port 9123): "
if curl -s http://localhost:9123/health >/dev/null 2>&1 || curl -s http://localhost:9123 >/dev/null 2>&1; then
  echo "✓"
else
  echo "⚠ (may be starting)"
fi

echo -n "    - GraphQL (port 8000): "
if curl -s -X POST http://localhost:8000/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{chainIdentifier}"}' >/dev/null 2>&1; then
  echo "✓"
else
  echo "⚠ (may still be indexing)"
fi

echo ""
echo ">>> [4/5] Publishing Move package..."
PUBLISH_OUTPUT=$(docker compose run --rm \
  -v "$PWD/move/financial_audit:/workspace/move/financial_audit" \
  --entrypoint="" \
  sui-cli bash -c '
    set -euo pipefail
    RPC="http://sui-localnet:9000"
    echo -e "y\n\n0" | sui client new-env --alias local --rpc "$RPC" >/dev/null 2>&1 || true
    sui client switch --env local >/dev/null
    sui client faucet --url http://sui-localnet:9123/gas >/dev/null
    cd /workspace/move/financial_audit
    sui move build
    sui client publish --gas-budget 100000000 .
  ')

echo "$PUBLISH_OUTPUT" | sed -E 's/^/    /'

PKG_ID=$(echo "$PUBLISH_OUTPUT" | grep -oE 'PackageID: 0x[0-9a-fA-F]+' | awk '{print $2}' | tail -n 1)
if [[ -z "${PKG_ID:-}" ]]; then
  echo "ERROR: Failed to extract Package ID from publish output."
  exit 1
fi
echo ">>> Package ID: $PKG_ID"

echo ""
echo ">>> [5/5] Finalizing..."
echo ""

# Set a placeholder for TRAIL_ID so config file can be created
TRAIL_ID=""

echo ""
echo "=============================================================="
echo "  ✓ SUCCESS: Sui GraphQL + General-Purpose Indexer Ready!"
echo "=============================================================="
echo ""
echo "📦 Package ID:      $PKG_ID"
echo "🔍 AuditTrail ID:   $TRAIL_ID"
echo ""

# Save config to file for easy access
CONFIG_FILE="$PROJECT_ROOT/.sui-config"
cat > "$CONFIG_FILE" <<EOF
# Sui Local Network Configuration
# Official GraphQL + General-Purpose Indexer Stack
# Generated: $(date)
export SUI_PACKAGE_ID=$PKG_ID
export AUDIT_TRAIL_OBJ_ID=""
export SUI_RPC_URL=http://localhost:9000
export SUI_GRPC_URL=http://localhost:9184
export SUI_FAUCET_URL=http://localhost:9123
export SUI_GRAPHQL_URL=http://localhost:8000/graphql
# Run ./init_audit_trail.sh to initialize the AuditTrail and populate AUDIT_TRAIL_OBJ_ID
EOF

echo "💾 Configuration saved to: .sui-config"
echo ""
echo "🌐 Service Endpoints:"
echo "   - GraphQL RPC (recommended):  http://localhost:8000/graphql"
echo "   - pgAdmin (database GUI):     http://localhost:5050"
echo "   - JSON-RPC (deprecated):      http://localhost:9000"
echo "   - gRPC (future):              http://localhost:9184"
echo "   - Faucet:                     http://localhost:9123"
echo "   - PostgreSQL:                 postgresql://sui:sui@localhost:5432/sui_indexer"
echo ""
echo "💡 Next Steps:"
echo "   1. Initialize AuditTrail:   ./init_audit_trail.sh"
echo "   2. Load config:             source .sui-config"
echo "   3. View config:             ./get_config.sh"
echo ""
echo "📝 Other Commands:"
echo "   - View logs:        docker compose logs -f sui-localnet"
echo "   - GraphQL logs:     docker compose logs -f sui-graphql"
echo "   - Indexer logs:     docker compose logs -f sui-indexer"
echo "   - Stop network:     docker compose down"
echo "   - Reset network:    docker compose down -v && ./start.sh"
echo ""

