# QuantPricer Backend (FREE Deployment)

## Deployment Options (All Free!)

### Option 1: Render (Recommended - Completely Free)
1. Create account at [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set source directory to `backend`
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Deploy (no environment variables needed)

### Option 2: Railway (Free Tier)
1. Create account at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Select the `backend` directory as the source
4. Deploy (Railway will auto-detect Python)

### Option 3: Heroku (Free Tier - Limited)
1. Create account at [heroku.com](https://heroku.com)
2. Install Heroku CLI
3. Create app: `heroku create your-app-name`
4. Deploy: `git push heroku main`

### Environment Variables
- `PORT`: Port number (auto-set by platform)
- No database configuration needed (using SQLite)

### Local Development
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
