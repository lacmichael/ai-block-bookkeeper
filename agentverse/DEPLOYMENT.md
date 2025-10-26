# Agentverse Deployment Configuration

## 🚀 Zero-Configuration Deployment (Recommended)

**Deploy immediately without any environment variables!**

```bash
cd agentverse
python deploy_no_env.py
```

This runs all agents in **mock mode** - perfect for:
- ✅ Agentverse deployment
- ✅ Demo and testing  
- ✅ Development without external dependencies
- ✅ Showcasing agent capabilities

### What Mock Mode Provides

- **AI Processing**: Simulates document extraction with realistic data
- **Blockchain**: Simulates Sui transaction posting with mock digests
- **Database**: Simulates data persistence and retrieval
- **Reconciliation**: Simulates invoice-to-payment matching
- **Agent Communication**: Full functionality between agents

## 🔧 Environment Variables (Optional)

If you want to enable real services, create a `.env` file with the following configuration:

```bash
# Agent Configuration
AUDIT_AGENT_SEED=audit-verification-agent-seed-12345
AUDIT_AGENT_PORT=8001
AUDIT_AGENT_ENDPOINT=127.0.0.1

DOCUMENT_AGENT_SEED=document-processing-agent-seed-12345
DOCUMENT_AGENT_PORT=8003
DOCUMENT_AGENT_ENDPOINT=127.0.0.1

RECONCILIATION_AGENT_SEED=reconciliation-agent-seed-12345
RECONCILIATION_AGENT_PORT=8004
RECONCILIATION_AGENT_ENDPOINT=127.0.0.1

# External Service Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Sui Blockchain Configuration
SUI_PACKAGE_ID=your_sui_package_id
SUI_MODULE=financial_audit
SUI_FUNCTION=record_transaction_fields
AUDIT_TRAIL_OBJ_ID=your_audit_trail_object_id
SENDER_ADDRESS=your_sender_address
GAS_BUDGET=100000000
USE_SUI_DOCKER_CLI=true
SUI_RPC_URL=http://127.0.0.1:9000

# Agent Communication
AUDIT_AGENT_ADDRESS=agent1q...
DOCUMENT_AGENT_ADDRESS=agent1q...
RECONCILIATION_AGENT_ADDRESS=agent1q...
```

## Deployment Steps

### 1. Prepare Agents for Agentverse

Each agent is optimized for Agentverse deployment with:
- ASI:One Chat Protocol compatibility
- Rich metadata for discoverability
- Health check endpoints
- Error handling and logging
- Search-optimized README files

### 2. Register Agents on Agentverse

Use the Agentverse API to register each agent:

```bash
# Register Audit Verification Agent
curl -X POST https://api.agentverse.ai/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AuditVerificationAgent",
    "description": "AI-Powered Blockchain Transaction Auditor for Financial Documents",
    "category": "Finance",
    "tags": ["blockchain", "audit", "verification", "financial", "transactions", "Sui"],
    "endpoint": "http://your-server:8001/submit",
    "protocols": ["ASI_CHAT_PROTOCOL"],
    "readme": "README_audit_verification_agent.md"
  }'

# Register Document Processing Agent
curl -X POST https://api.agentverse.ai/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DocumentProcessingAgent", 
    "description": "AI-Powered Financial Document Analyzer and Business Event Generator",
    "category": "Finance",
    "tags": ["document processing", "AI extraction", "financial documents", "invoice processing", "Claude AI"],
    "endpoint": "http://your-server:8003/submit",
    "protocols": ["ASI_CHAT_PROTOCOL"],
    "readme": "README_document_processing_agent.md"
  }'

# Register Reconciliation Agent
curl -X POST https://api.agentverse.ai/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ReconciliationAgent",
    "description": "Automated Financial Transaction Matcher and Reconciliation Engine", 
    "category": "Finance",
    "tags": ["reconciliation", "transaction matching", "invoice matching", "payment reconciliation", "financial matching"],
    "endpoint": "http://your-server:8004/submit",
    "protocols": ["ASI_CHAT_PROTOCOL"],
    "readme": "README_reconciliation_agent.md"
  }'
```

### 3. Deploy Agent Infrastructure

Deploy the agents on your infrastructure:

```bash
# Start Audit Verification Agent
python audit_verification_agent.py

# Start Document Processing Agent  
python document_processing_agent.py

# Start Reconciliation Agent
python reconciliation_agent.py
```

### 4. Verify Agent Registration

Check agent status on Agentverse:

```bash
# Check agent health
curl https://api.agentverse.ai/agents/{agent_id}/health

# Test agent communication
curl -X POST https://api.agentverse.ai/agents/{agent_id}/query \
  -H "Content-Type: application/json" \
  -d '{"type": "HealthQuery"}'
```

## Agent Optimization Features

### Search Optimization
- **Rich Metadata**: Each agent includes comprehensive metadata for search indexing
- **Keyword-Rich Descriptions**: Optimized descriptions with relevant financial keywords
- **Category Classification**: Proper categorization for better discoverability
- **Tag Optimization**: Strategic tagging for search relevance

### ASI:One Compatibility
- **Chat Protocol Integration**: Full ASI:One Chat Protocol support
- **Message Models**: Properly structured message models for agent communication
- **Query Handlers**: Health check and status query endpoints
- **Error Handling**: Comprehensive error handling and response formatting

### Performance Monitoring
- **Health Endpoints**: Real-time health monitoring for each agent
- **Performance Metrics**: Built-in performance tracking and reporting
- **Status Reporting**: Detailed status information for monitoring systems
- **Error Logging**: Comprehensive logging for debugging and monitoring

## Agent Communication Flow

```
Document Processing Agent
    ↓ (AuditVerificationRequest)
Audit Verification Agent
    ↓ (AuditVerificationResponse)
Document Processing Agent
    ↓ (ReconciliationRequest)
Reconciliation Agent
    ↓ (ReconciliationResponse)
Document Processing Agent
```

## Monitoring and Maintenance

### Health Monitoring
- Monitor agent health endpoints regularly
- Track processing success rates
- Monitor blockchain posting success
- Track reconciliation accuracy

### Performance Optimization
- Optimize AI processing times
- Monitor blockchain transaction costs
- Track reconciliation match rates
- Optimize agent communication latency

### Security Considerations
- Secure API key management
- Blockchain wallet security
- Database access controls
- Agent communication encryption

## Troubleshooting

### Common Issues
- **Agent Registration Failures**: Check endpoint accessibility and configuration
- **Communication Errors**: Verify agent addresses and network connectivity
- **Blockchain Posting Failures**: Check Sui configuration and wallet funding
- **AI Processing Errors**: Verify Anthropic API key and quota limits

### Support Resources
- Agentverse Documentation: https://docs.agentverse.ai
- uAgents Framework: https://docs.uagents.ai
- Sui Blockchain: https://docs.sui.io
- Anthropic API: https://docs.anthropic.com
