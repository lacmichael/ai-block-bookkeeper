# document-agent

This is the document-agent package for Railway deployment.

## Files
- `Procfile` - Railway startup command
- `requirements.txt` - Python dependencies  
- `railway.json` - Railway configuration
- `*.py` - Agent code

## Deploy to Railway
1. Go to https://railway.app
2. Create new project
3. Deploy from GitHub repo
4. Set Root Directory to: `agentverse/document-agent`
5. Deploy!

## Test
After deployment, test with:
```bash
curl https://your-app.up.railway.app/health
```

