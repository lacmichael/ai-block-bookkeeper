#!/usr/bin/env bash
# init_audit_trail.sh - Initialize the AuditTrail object

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Get package ID from argument or config
if [[ -n "${1:-}" ]]; then
    PKG_ID="$1"
else
    if [[ -f ".sui-config" ]]; then
        source .sui-config
        PKG_ID="$SUI_PACKAGE_ID"
    else
        echo "ERROR: No package ID provided and no .sui-config found"
        echo "Usage: ./init_audit_trail.sh <PACKAGE_ID>"
        exit 1
    fi
fi

if [[ -z "$PKG_ID" ]]; then
    echo "ERROR: Package ID is empty"
    exit 1
fi

echo "Initializing AuditTrail for package: $PKG_ID"
echo ""

# Run the initialization
echo ">>> Calling init_audit_trail..."
docker compose exec sui-cli bash -c "
    sui client switch --env local 2>/dev/null || echo -e 'y\n\n0' | sui client new-env --alias local --rpc http://sui-localnet:9000 >/dev/null 2>&1
    sui client faucet --url http://sui-localnet:9123/gas >/dev/null 2>&1 || true
    sui client call \
        --package $PKG_ID \
        --module financial_audit \
        --function init_audit_trail \
        --args '[99,111,109,112,97,110,121,95,49,50,51]' \
        --gas-budget 100000000
" 2>&1 | tee /tmp/init_output.txt

echo ""
echo ">>> Extracting AuditTrail ID..."

# Extract the shared object ID from output
TRAIL_ID=$(grep -oE 'ObjectID: 0x[0-9a-fA-F]+' /tmp/init_output.txt | awk '{print $2}' | head -n 1)

if [[ -z "${TRAIL_ID:-}" ]]; then
    echo "ERROR: Failed to extract AuditTrail object ID"
    echo "Check output above for errors"
    exit 1
fi

echo "✓ AuditTrail ID: $TRAIL_ID"
echo ""

# Update the config file
if [[ -f ".sui-config" ]]; then
    echo ">>> Updating .sui-config..."
    sed -i.bak "s|export AUDIT_TRAIL_OBJ_ID=.*|export AUDIT_TRAIL_OBJ_ID=$TRAIL_ID|" .sui-config
    rm -f .sui-config.bak
    echo "✓ Configuration updated"
else
    echo ">>> Creating .sui-config..."
    cat > .sui-config <<EOF
# Sui Local Network Configuration
# Generated: $(date)
export SUI_PACKAGE_ID=$PKG_ID
export AUDIT_TRAIL_OBJ_ID=$TRAIL_ID
export SUI_RPC_URL=http://localhost:9000
export SUI_FAUCET_URL=http://localhost:9123
export SUI_GRAPHQL_URL=http://localhost:8000/graphql
EOF
    echo "✓ Configuration created"
fi

echo ""
echo "=================================================="
echo "  ✓ AuditTrail Initialized!"
echo "=================================================="
echo ""
echo "📦 Package ID:      $PKG_ID"
echo "🔍 AuditTrail ID:   $TRAIL_ID"
echo ""
echo "To load configuration:"
echo "  source .sui-config"
echo ""

