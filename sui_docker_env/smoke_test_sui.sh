#!/usr/bin/env bash
# smoke_test_sui.sh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo ">>> [1/7] Building images"
docker compose build

echo ">>> [2/7] Starting Sui localnet"
docker compose up -d sui-localnet

echo ">>> Waiting for sui-localnet to be healthy..."
for i in $(seq 1 60); do
  status=$(docker compose ps -q sui-localnet | xargs docker inspect --format='{{json .State.Health.Status}}' 2>/dev/null || echo '"starting"')
  if [[ "$status" == "\"healthy\"" ]]; then
    echo ">>> sui-localnet is healthy"
    break
  fi
  sleep 1
  if [[ $i -eq 60 ]]; then
    echo "ERROR: sui-localnet did not become healthy in time."
    docker compose logs sui-localnet | tail -n 100
    exit 1
  fi
done

echo ">>> [3/7] Verifying JSON-RPC on localhost:9000"
curl -s -X POST http://localhost:9000 \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"sui_getTotalTransactionBlocks","params":[]}' >/dev/null

echo ">>> [4/7] Publishing Move package and initializing AuditTrail"
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

INIT_OUTPUT=$(docker compose run --rm --entrypoint="" sui-cli bash -c "
  set -euo pipefail
  sui client switch --env local >/dev/null 2>&1 || echo -e 'y\n\n0' | sui client new-env --alias local --rpc http://sui-localnet:9000 >/dev/null 2>&1
  sui client call \
    --package $PKG_ID \
    --module financial_audit \
    --function init_audit_trail \
    --args \"b'company_123'\" \
    --gas-budget 100000000
")
echo \"$INIT_OUTPUT\" | sed -E 's/^/    /'

TRAIL_ID=$(echo "$INIT_OUTPUT" | grep -oE 'ObjectID: 0x[0-9a-fA-F]+' | awk '{print $2}' | grep -v 'UpgradeCap' | head -n 1)
if [[ -z "${TRAIL_ID:-}" ]]; then
  echo "ERROR: Failed to extract AuditTrail object ID."
  exit 1
fi
echo ">>> AuditTrail Object ID: $TRAIL_ID"

echo ">>> [5/7] Recording a sample transaction"
RECORD_OUTPUT=$(docker compose run --rm --entrypoint="" sui-cli bash -c "
  set -euo pipefail
  sui client switch --env local >/dev/null 2>&1 || echo -e 'y\n\n0' | sui client new-env --alias local --rpc http://sui-localnet:9000 >/dev/null 2>&1
  sui client call \
    --package $PKG_ID \
    --module financial_audit \
    --function record_transaction_fields \
    --args \
      $TRAIL_ID \
      \"b'tx_0001_uuid_bytes'\" \
      499900 \
      1730059200 \
      0x000102030405060708090a0b0c0d0e0f000102030405060708090a0b0c0d0e0f \
      \"b'Software:Cloud'\" \
      1 \
    --gas-budget 100000000
")
echo \"$RECORD_OUTPUT\" | sed -E 's/^/    /'

DIGEST=$(echo "$RECORD_OUTPUT" | grep -oE 'Digest: [A-Za-z0-9]+' | awk '{print $2}' | head -n 1)
if [[ -z "${DIGEST:-}" ]]; then
  echo "ERROR: Failed to extract transaction digest."
  exit 1
fi
echo ">>> Recorded transaction digest: $DIGEST"

echo ">>> [6/7] Querying TransactionRecorded events"
EVENTS=$(curl -s -X POST http://localhost:9000 -H 'content-type: application/json' -d "{
  \"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"suix_queryEvents\",
  \"params\":[{\"MoveEventType\":\"$PKG_ID::financial_audit::TransactionRecorded\"}, null, 50, true]
}")
echo "$EVENTS" | sed -E 's/^/    /'

echo "$EVENTS" | grep -q "tx_0001_uuid_bytes" && echo ">>> ✓ Event contains tx_0001_uuid_bytes" || {
  echo "ERROR: TransactionRecorded event was not found or does not contain expected tx_id."; exit 1; }

echo ">>> [7/7] SUCCESS: Sui Docker environment is healthy and contract works."
