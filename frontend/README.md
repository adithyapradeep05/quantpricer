# QuantPricer Frontend

## Deployment Setup

### Prerequisites
1. Deploy your FastAPI backend first (see backend/README.md)
2. Get your backend URL (e.g., from Railway, Render, or similar)

### Environment Variables
Create a `.env.local` file in the frontend directory:
```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

### Vercel Deployment
1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set the environment variable `NEXT_PUBLIC_API_URL` in Vercel dashboard
4. Deploy

### Local Development
```bash
npm install
npm run dev
```
