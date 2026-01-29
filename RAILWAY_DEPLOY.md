# 🚂 Railway Deployment Guide

## Quick Deploy (Recommended)

1. **Go to Railway**: https://railway.app
2. **Sign in** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Authorize Railway** to access your GitHub
6. **Push this code to GitHub** (see below)
7. **Select the repository** in Railway
8. **Add Environment Variable**:
   - Variable: `ANTHROPIC_API_KEY`
   - Value: Your Anthropic API key
9. **Deploy!** Railway will automatically:
   - Detect Python
   - Install dependencies
   - Run the app

## Step 1: Push to GitHub

```bash
# Create a new repository on GitHub (https://github.com/new)
# Then run these commands:

git remote add origin https://github.com/YOUR_USERNAME/website-evolution-tracker.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Railway

### Option A: Via Railway Dashboard (Easiest)

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway will auto-detect the configuration

### Option B: Via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variable
railway variables set ANTHROPIC_API_KEY=your-key-here

# Deploy
railway up
```

## Step 3: Configure Environment Variables

In Railway dashboard:
1. Go to your project
2. Click **"Variables"** tab
3. Add these variables:
   - **ANTHROPIC_API_KEY**: Your Anthropic API key (required)

## Step 4: Get Your URL

Railway will automatically assign you a URL like:
```
https://your-app.up.railway.app
```

You can also add a custom domain in the Railway settings.

## Expected Build Output

Railway will:
1. ✅ Detect Python 3.11
2. ✅ Install dependencies from `requirements.txt`
3. ✅ Run via Gunicorn (specified in `Procfile`)
4. ✅ Expose on Railway's assigned port

## Troubleshooting

### Build fails
- Check that all files are committed to git
- Verify `requirements.txt` is valid
- Check Railway logs in dashboard

### App crashes on start
- Verify `ANTHROPIC_API_KEY` is set
- Check Railway logs for errors
- Ensure Python version matches (3.11)

### App is slow
- First request may be slow (cold start)
- Consider upgrading Railway plan for better performance
- Web Archive API can be slow

## Cost

- **Hobby Plan**: $5/month (includes 500 hours, $0.000231/GB-hour)
- **Pro Plan**: $20/month (unlimited)

The Hobby plan should be sufficient for this app.

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `PORT` | No | Auto-set by Railway |

## Files for Railway

These files are configured for Railway:

- ✅ `Procfile` - Tells Railway to use Gunicorn
- ✅ `runtime.txt` - Specifies Python 3.11
- ✅ `railway.toml` - Railway configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `.gitignore` - Files to ignore

## Post-Deployment

After deployment:
1. Visit your Railway URL
2. Try analyzing: `www.myadorabook.com`
3. Check logs if issues occur
4. Share your link!

## Custom Domain (Optional)

1. In Railway dashboard, go to **Settings**
2. Click **"Generate Domain"** or add custom domain
3. For custom domain:
   - Add CNAME record in your DNS
   - Point to Railway domain

## Monitoring

Railway provides:
- 📊 Real-time logs
- 📈 Resource usage graphs
- 🔄 Deployment history
- ⚡ Auto-restart on crash

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Anthropic API: https://docs.anthropic.com
