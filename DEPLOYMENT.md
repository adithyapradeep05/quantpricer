# QuantPricer Deployment Guide (100% FREE)

This guide will help you deploy your QuantPricer application to production using completely free hosting services.

## Architecture Overview

- **Frontend**: Next.js application deployed on Vercel (FREE)
- **Backend**: FastAPI application deployed on Render (FREE)
- **Database**: SQLite (included with backend, no separate database needed)

## Step 1: Deploy Backend (FREE on Render)

### Render (Recommended - Completely Free)

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub (free tier available)

2. **Deploy Backend**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Set source directory to `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Configure Environment**
   - No environment variables needed (using SQLite)
   - Render will provide the `PORT` automatically

4. **Get Backend URL**
   - Copy the generated URL (e.g., `https://your-app.onrender.com`)

### Alternative: Railway (Free Tier)
- Railway also has a free tier but with limitations
- Render is more generous for personal projects

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Deploy Backend**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Set source directory to `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Configure Environment**
   - Add environment variable: `DATABASE_URL`
   - Render will provide PostgreSQL

## Step 2: Deploy Frontend (FREE on Vercel)

### Deploy to Vercel (Completely Free)

1. **Create Vercel Account**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub (free tier available)

2. **Deploy Frontend**
   - Click "New Project"
   - Import your GitHub repository
   - Set root directory to `frontend`
   - Vercel will auto-detect Next.js

3. **Configure Environment**
   - Go to project settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = your backend URL from Step 1

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your frontend

## Step 3: Update CORS (if needed)

If you get CORS errors, update your backend's CORS configuration in `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 4: Test Your Deployment

1. **Test Backend**
   - Visit `https://your-backend-url/docs` for API documentation
   - Test the health endpoint: `https://your-backend-url/healthz`

2. **Test Frontend**
   - Visit your Vercel URL
   - Try calculating option prices
   - Check that charts and visualizations work

## Environment Variables Summary

### Backend
- `PORT`: Port number (auto-set by platform)
- No database configuration needed (using SQLite)

### Frontend
- `NEXT_PUBLIC_API_URL`: Your backend URL (e.g., `https://your-app.onrender.com`)

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Update CORS configuration in backend
   - Ensure frontend URL is in allowed origins

2. **Database Connection Errors**
   - SQLite database is included with the backend
   - No separate database setup needed

3. **Build Errors**
   - Check Python version compatibility
   - Verify all dependencies are in `requirements.txt`

4. **API Connection Errors**
   - Verify `NEXT_PUBLIC_API_URL` is correct
   - Check backend is running and accessible

### Support

- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Vercel**: [vercel.com/docs](https://vercel.com/docs)
- **Render**: [render.com/docs](https://render.com/docs)

## Cost: COMPLETELY FREE! 🎉

- **Render**: Free tier (750 hours/month, perfect for personal projects)
- **Vercel**: Free tier (unlimited personal projects)
- **Total Cost**: $0/month

### Free Tier Limits:
- **Render**: 750 hours/month (about 31 days)
- **Vercel**: 100GB bandwidth/month, unlimited builds
- **Perfect for**: Personal projects, portfolios, demos

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to Git
2. **CORS**: Restrict origins to your frontend domain only
3. **Database**: SQLite is perfect for personal projects
4. **HTTPS**: All platforms provide HTTPS by default
5. **Free Tier**: Perfect for learning and personal projects
