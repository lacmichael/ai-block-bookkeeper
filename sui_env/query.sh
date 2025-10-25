#!/usr/bin/env bash
# Quick query helper for local Sui network

RPC_URL="http://localhost:9000"
GRAPHQL_URL="http://localhost:8000/graphql"

case "$1" in
  "total")
    echo "Getting total transactions..."
    curl -s -X POST "$RPC_URL" \
      -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"sui_getTotalTransactionBlocks","params":[]}' | jq
    ;;
  
  "events")
    if [ -z "$2" ]; then
      echo "Usage: ./query.sh events <PACKAGE_ID>"
      exit 1
    fi
    echo "Querying events for package $2..."
    curl -s -X POST "$RPC_URL" \
      -H 'Content-Type: application/json' \
      -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"suix_queryEvents\",\"params\":[{\"MoveModule\":{\"package\":\"$2\",\"module\":\"financial_audit\"}},null,50,false]}" | jq
    ;;
  
  "tx")
    if [ -z "$2" ]; then
      echo "Usage: ./query.sh tx <TRANSACTION_DIGEST>"
      exit 1
    fi
    echo "Getting transaction $2..."
    curl -s -X POST "$RPC_URL" \
      -H 'Content-Type: application/json' \
      -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"sui_getTransactionBlock\",\"params\":[\"$2\",{\"showInput\":true,\"showEffects\":true,\"showEvents\":true,\"showObjectChanges\":true,\"showBalanceChanges\":true}]}" | jq
    ;;
  
  "object")
    if [ -z "$2" ]; then
      echo "Usage: ./query.sh object <OBJECT_ID>"
      exit 1
    fi
    echo "Getting object $2..."
    curl -s -X POST "$RPC_URL" \
      -H 'Content-Type: application/json' \
      -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"sui_getObject\",\"params\":[\"$2\",{\"showType\":true,\"showContent\":true,\"showOwner\":true}]}" | jq
    ;;
  
  "audit-trail")
    if [ -z "$2" ]; then
      echo "Usage: ./query.sh audit-trail <AUDIT_TRAIL_ID>"
      exit 1
    fi
    echo "Getting AuditTrail object $2..."
    curl -s -X POST "$RPC_URL" \
      -H 'Content-Type: application/json' \
      -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"sui_getObject\",\"params\":[\"$2\",{\"showType\":true,\"showContent\":true,\"showOwner\":true}]}" | jq
    ;;
  
  "gql")
    if [ -z "$2" ]; then
      echo "Usage: ./query.sh gql '<GRAPHQL_QUERY>'"
      echo "Example: ./query.sh gql '{chainIdentifier}'"
      exit 1
    fi
    echo "Executing GraphQL query..."
    curl -s -X POST "$GRAPHQL_URL" \
      -H 'Content-Type: application/json' \
      -d "{\"query\":\"$2\"}" | jq
    ;;
  
  "gql-events")
    if [ -z "$2" ]; then
      echo "Usage: ./query.sh gql-events <PACKAGE_ID>"
      exit 1
    fi
    echo "Querying events via GraphQL for package $2..."
    query='{ events(first: 50, filter: {eventType: "'"$2"'::financial_audit::TransactionRecorded"}) { nodes { sendingModule { package { address } name } timestamp bcs } pageInfo { hasNextPage endCursor } } }'
    curl -s -X POST "$GRAPHQL_URL" \
      -H 'Content-Type: application/json' \
      -d "{\"query\":$(echo "$query" | jq -Rs .)}" | jq
    ;;
  
  "gql-txs")
    echo "Querying recent transactions via GraphQL..."
    query='{ transactionBlocks(first: 10) { nodes { digest sender { address } gasInput { gasSponsor { address } gasPrice } effects { status } } pageInfo { hasNextPage endCursor } } }'
    curl -s -X POST "$GRAPHQL_URL" \
      -H 'Content-Type: application/json' \
      -d "{\"query\":$(echo "$query" | jq -Rs .)}" | jq
    ;;
  
  "gql-objects")
    if [ -z "$2" ]; then
      echo "Usage: ./query.sh gql-objects <OWNER_ADDRESS>"
      exit 1
    fi
    echo "Querying objects owned by $2 via GraphQL..."
    query='{ address(address: "'"$2"'") { objects(first: 20) { nodes { address version digest objectKind } pageInfo { hasNextPage } } } }'
    curl -s -X POST "$GRAPHQL_URL" \
      -H 'Content-Type: application/json' \
      -d "{\"query\":$(echo "$query" | jq -Rs .)}" | jq
    ;;
  
  "gql-package")
    if [ -z "$2" ]; then
      echo "Usage: ./query.sh gql-package <PACKAGE_ID>"
      exit 1
    fi
    echo "Querying package info via GraphQL..."
    query='{ object(address: "'"$2"'") { address version asMovePackage { modules { name fileFormatVersion bytes } } } }'
    curl -s -X POST "$GRAPHQL_URL" \
      -H 'Content-Type: application/json' \
      -d "{\"query\":$(echo "$query" | jq -Rs .)}" | jq
    ;;
  
  "gql-balance")
    if [ -z "$2" ]; then
      echo "Usage: ./query.sh gql-balance <ADDRESS>"
      exit 1
    fi
    echo "Querying balance for $2 via GraphQL..."
    query='{ address(address: "'"$2"'") { balance { totalBalance } coins { nodes { coinType coinBalance } } } }'
    curl -s -X POST "$GRAPHQL_URL" \
      -H 'Content-Type: application/json' \
      -d "{\"query\":$(echo "$query" | jq -Rs .)}" | jq
    ;;
  
  "gql-chain")
    echo "Querying chain information via GraphQL..."
    query='{ chainIdentifier epoch { epochId referenceGasPrice systemStateVersion } protocolConfig { protocolVersion } serviceConfig { maxQueryDepth maxQueryNodes maxPageSize } }'
    curl -s -X POST "$GRAPHQL_URL" \
      -H 'Content-Type: application/json' \
      -d "{\"query\":$(echo "$query" | jq -Rs .)}" | jq
    ;;
  
  *)
    echo "Sui Local Network Query Tool"
    echo ""
    echo "Usage (Legacy JSON-RPC - Deprecated):"
    echo "  ./query.sh total                          - Get total transactions"
    echo "  ./query.sh events <PACKAGE_ID>            - Get all events from package"
    echo "  ./query.sh tx <DIGEST>                    - Get transaction details"
    echo "  ./query.sh object <OBJECT_ID>             - Get object details"
    echo "  ./query.sh audit-trail <AUDIT_TRAIL_ID>   - Get AuditTrail object"
    echo ""
    echo "Usage (GraphQL RPC - Recommended):"
    echo "  ./query.sh gql '<QUERY>'                  - Execute custom GraphQL query"
    echo "  ./query.sh gql-chain                      - Get chain info and service config"
    echo "  ./query.sh gql-txs                        - Get recent transactions"
    echo "  ./query.sh gql-events <PACKAGE_ID>        - Get events from package"
    echo "  ./query.sh gql-objects <OWNER_ADDRESS>    - Get objects owned by address"
    echo "  ./query.sh gql-package <PACKAGE_ID>       - Get package info and modules"
    echo "  ./query.sh gql-balance <ADDRESS>          - Get address balance and coins"
    echo ""
    echo "Examples:"
    echo "  # Chain information"
    echo "  ./query.sh gql-chain"
    echo ""
    echo "  # Recent transactions with pagination"
    echo "  ./query.sh gql-txs"
    echo ""
    echo "  # Events from your package"
    echo "  ./query.sh gql-events 0xabcd1234..."
    echo ""
    echo "  # Objects owned by an address"
    echo "  ./query.sh gql-objects 0x1234..."
    echo ""
    echo "  # Custom GraphQL query"
    echo "  ./query.sh gql '{ transactionBlocks(first: 5) { nodes { digest } } }'"
    echo ""
    echo "  # Complex query with filtering"
    echo "  ./query.sh gql '{ events(first: 10, filter: {sender: \"0x123\"}) { nodes { timestamp } } }'"
    exit 1
    ;;
esac

