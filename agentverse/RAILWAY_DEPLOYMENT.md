# 🚀 Railway Deployment Guide

## ✅ **Ready to Deploy!**

Your agent packages are ready for Railway deployment:

- ✅ `audit-agent/` - Audit Verification Agent
- ✅ `document-agent/` - Document Processing Agent  
- ✅ `reconciliation-agent/` - Reconciliation Agent

Each package contains:
- `Procfile` - Tells Railway how to run the agent
- `requirements.txt` - Python dependencies
- Agent Python file - Your agent code

## 🚂 **Deploy to Railway (5 minutes)**

### **Step 1: Go to Railway**
```
https://railway.app
```

### **Step 2: Sign Up**
- Click "Sign Up"
- Choose "Sign up with GitHub"
- Authorize Railway to access your GitHub

### **Step 3: Create 3 Projects**

**For Audit Agent:**
1. Click "New Project"
2. Choose "Deploy from GitHub repo"
3. Select your `ai-block-bookkeeper` repository
4. **Important**: Set "Root Directory" to `agentverse/audit-agent`
5. Click "Deploy"

**For Document Agent:**
1. Click "New Project" 
2. Choose "Deploy from GitHub repo"
3. Select your `ai-block-bookkeeper` repository
4. **Important**: Set "Root Directory" to `agentverse/document-agent`
5. Click "Deploy"

**For Reconciliation Agent:**
1. Click "New Project"
2. Choose "Deploy from GitHub repo" 
3. Select your `ai-block-bookkeeper` repository
4. **Important**: Set "Root Directory" to `agentverse/reconciliation-agent`
5. Click "Deploy"

### **Step 4: Get Your Public URLs**

After deployment, Railway will give you URLs like:
- `https://audit-agent-production.up.railway.app`
- `https://document-agent-production.up.railway.app`
- `https://reconciliation-agent-production.up.railway.app`

### **Step 5: Test Your Agents**

Test each agent with:
```bash
# Test health endpoint
curl https://audit-agent-production.up.railway.app/health

# Test chat protocol
curl -X POST https://audit-agent-production.up.railway.app/submit \
  -H "Content-Type: application/json" \
  -d '{"message": "help", "user_id": "test"}'
```

## 🎯 **Alternative: Render (Also Easy)**

### **Step 1: Go to Render**
```
https://render.com
```

### **Step 2: Create 3 Web Services**

**For each agent:**
1. Click "New Web Service"
2. Connect your GitHub repo
3. **Important**: Set "Root Directory" to `agentverse/audit-agent` (or document-agent, reconciliation-agent)
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `python audit_verification_agent.py` (or appropriate file)
6. Click "Create Web Service"

### **Step 3: Get URLs**
- `https://audit-agent.onrender.com`
- `https://document-agent.onrender.com`
- `https://reconciliation-agent.onrender.com`

## 🔧 **What Each Agent Does**

### **Audit Agent** (`audit-agent/`)
- **Port**: 8001
- **Function**: Posts transactions to blockchain
- **Chat Commands**: `help`, `status`, `capabilities`
- **Mock Mode**: Simulates Sui blockchain posting

### **Document Agent** (`document-agent/`)
- **Port**: 8003  
- **Function**: AI document processing
- **Chat Commands**: `help`, `status`, `capabilities`, `process document`
- **Mock Mode**: Simulates Claude AI processing

### **Reconciliation Agent** (`reconciliation-agent/`)
- **Port**: 8004
- **Function**: Transaction matching
- **Chat Commands**: `help`, `status`, `capabilities`, `stats`
- **Mock Mode**: Simulates database matching

## 📋 **Next Steps**

1. **Deploy all 3 agents** to Railway/Render
2. **Get public URLs** for each agent
3. **Test agents** are reachable from internet
4. **Register agents** on Agentverse with public URLs
5. **Share your agents** with the community!

## 🎉 **Success!**

Once deployed, you'll have:
- ✅ **3 public HTTPS endpoints**
- ✅ **ASI:One Chat Protocol** support
- ✅ **Health monitoring** endpoints
- ✅ **Mock mode** (no external dependencies)
- ✅ **Ready for Agentverse** registration

**Your agents will be discoverable and usable by anyone on Agentverse!** 🚀
