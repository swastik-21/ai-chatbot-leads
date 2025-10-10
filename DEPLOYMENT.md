# Deployment Guide - AI Chatbot Leads

This guide covers the most cost-effective deployment options for your AI Chatbot Leads system.

## 🚀 Deployment Options (Ranked by Cost)

### 1. **Render (Recommended - FREE Tier Available)**
**Cost**: FREE for basic usage, $7/month for paid plans

**Steps:**
1. Go to [render.com](https://render.com) and sign up
2. Connect your GitHub account
3. Click "New +" → "Web Service"
4. Connect your `ai-chatbot-leads` repository
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python manage.py migrate && python manage.py seed_faqs && gunicorn ai_chatbot_leads.wsgi:application --bind 0.0.0.0:$PORT`
   - **Environment Variables**:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `DJANGO_SECRET_KEY`: Generate a random secret key
     - `DEBUG`: `False`
     - `ALLOWED_HOSTS`: `*`

**Pros**: Free tier, easy setup, automatic deployments
**Cons**: Limited resources on free tier

### 2. **Railway (Very Cheap)**
**Cost**: $5/month for hobby plan

**Steps:**
1. Go to [railway.app](https://railway.app) and sign up
2. Connect your GitHub account
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `ai-chatbot-leads` repository
5. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DJANGO_SECRET_KEY`: Generate a random secret key
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `*`

**Pros**: Very cheap, good performance, easy scaling
**Cons**: Not free

### 3. **Heroku (Easy but More Expensive)**
**Cost**: $7/month for basic plan

**Steps:**
1. Install Heroku CLI: `brew install heroku/brew/heroku`
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=your-key
   heroku config:set DJANGO_SECRET_KEY=your-secret
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=*
   ```
5. Deploy: `git push heroku main`

**Pros**: Very easy, reliable
**Cons**: More expensive, no free tier

### 4. **DigitalOcean App Platform**
**Cost**: $5/month for basic plan

**Steps:**
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Create new app from GitHub
3. Select your repository
4. Configure environment variables
5. Deploy

**Pros**: Good performance, reliable
**Cons**: Not free

## 🔧 Pre-Deployment Setup

### 1. Update Requirements (if needed)
```bash
pip install --upgrade openai==1.0.0
```

### 2. Test Locally
```bash
python manage.py migrate
python manage.py seed_faqs
python manage.py runserver
```

### 3. Generate Secret Key
```python
import secrets
print(secrets.token_urlsafe(50))
```

## 🌐 Environment Variables

Set these in your deployment platform:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-proj-...` |
| `DJANGO_SECRET_KEY` | Django secret key | `generated-secret-key` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `*` or your domain |

## 📊 Cost Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| **Render** | ✅ Yes | $7/month | Getting started |
| **Railway** | ❌ No | $5/month | Production |
| **Heroku** | ❌ No | $7/month | Enterprise |
| **DigitalOcean** | ❌ No | $5/month | Scaling |

## 🎯 Recommended Deployment Flow

1. **Start with Render** (Free tier)
2. **Upgrade to Railway** if you need more resources ($5/month)
3. **Scale to DigitalOcean** for high traffic ($5/month)

## 🔍 Post-Deployment Testing

1. **Test API**: `curl https://your-app.railway.app/api/chat/ -X POST -H "Content-Type: application/json" -d '{"message": "Hello!"}'`
2. **Test Frontend**: Visit your app URL
3. **Test Lead Qualification**: Send a message with contact info
4. **Check Logs**: Monitor for any errors

## 🚨 Common Issues & Solutions

### OpenAI API Issues
- Ensure you're using `openai==1.0.0` for compatibility
- Check API key is correctly set
- Verify API key has sufficient credits

### Database Issues
- Ensure migrations run: `python manage.py migrate`
- Check database connection settings

### Static Files Issues
- Run: `python manage.py collectstatic --noinput`
- Ensure static files are served correctly

## 📈 Monitoring & Scaling

### Free Tier Limits
- **Render**: 750 hours/month, 512MB RAM
- **Railway**: No free tier, but very cheap

### Scaling Tips
- Use Redis for caching (Railway provides this)
- Implement database connection pooling
- Use CDN for static files
- Monitor API usage and costs

## 💡 Cost Optimization

1. **Use GPT-3.5-turbo** (cheapest model)
2. **Implement caching** (10-second cache already included)
3. **Optimize prompts** to reduce token usage
4. **Monitor usage** to avoid unexpected costs

Your AI chatbot is ready to deploy! Start with Render's free tier and scale as needed.



