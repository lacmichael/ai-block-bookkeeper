#!/usr/bin/env bash
# get_config.sh - Easily retrieve Sui network configuration

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$PROJECT_ROOT/.sui-config"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "ERROR: Configuration file not found."
    echo "Please run ./start.sh first to initialize the network."
    exit 1
fi

# Parse command
case "${1:-show}" in
    "show"|"")
        echo "Sui Local Network Configuration:"
        echo ""
        cat "$CONFIG_FILE" | grep -v "^#" | grep -v "^$"
        echo ""
        echo "💡 To use in your shell:"
        echo "   source sui_env/.sui-config"
        ;;
    
    "source"|"load")
        # Source the file to export variables
        source "$CONFIG_FILE"
        echo "Environment variables loaded:"
        echo "  SUI_PACKAGE_ID=$SUI_PACKAGE_ID"
        echo "  AUDIT_TRAIL_OBJ_ID=$AUDIT_TRAIL_OBJ_ID"
        ;;
    
    "package"|"pkg")
        source "$CONFIG_FILE"
        echo "$SUI_PACKAGE_ID"
        ;;
    
    "trail"|"audit")
        source "$CONFIG_FILE"
        echo "$AUDIT_TRAIL_OBJ_ID"
        ;;
    
    "env")
        # Output in a format suitable for .env files
        source "$CONFIG_FILE"
        echo "SUI_PACKAGE_ID=$SUI_PACKAGE_ID"
        echo "AUDIT_TRAIL_OBJ_ID=$AUDIT_TRAIL_OBJ_ID"
        echo "SUI_RPC_URL=$SUI_RPC_URL"
        echo "SUI_FAUCET_URL=$SUI_FAUCET_URL"
        echo "SUI_GRAPHQL_URL=$SUI_GRAPHQL_URL"
        ;;
    
    *)
        echo "Usage: ./get_config.sh [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  show           Show all configuration (default)"
        echo "  source|load    Source configuration into current shell"
        echo "  package|pkg    Output package ID only"
        echo "  trail|audit    Output audit trail ID only"
        echo "  env            Output in .env format"
        echo ""
        echo "Examples:"
        echo "  ./get_config.sh show"
        echo "  ./get_config.sh package"
        echo "  source <(./get_config.sh source)"
        echo "  ./get_config.sh env >> ../.env"
        ;;
esac

