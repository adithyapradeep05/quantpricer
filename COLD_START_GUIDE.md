# QuantPricer Cold-Start Handling System

This document describes the cold-start handling system implemented for QuantPricer to gracefully handle Render Free-tier cold starts and improve first-use UX.

## Features Implemented

### Backend (FastAPI)
- ✅ Lightweight `/health` endpoint that returns immediately
- ✅ Lazy initialization of heavy modules (first request only)
- ✅ Idempotency handling for POST `/price` with in-memory cache
- ✅ Binds to `0.0.0.0` and uses `PORT` from environment
- ✅ CORS configuration for frontend
- ✅ Procfile and render.yaml for deployment

### Frontend (Next.js/React)
- ✅ API client wrapper with non-blocking `/health` preflight
- ✅ "Waking server..." UI state after 1.2s threshold
- ✅ Exponential backoff (3 attempts) + jitter
- ✅ Long per-attempt timeout (30s) to ride out cold start
- ✅ `AbortController` support for cancellation
- ✅ Idempotency key generation per request
- ✅ `usePrice()` hook exposing `{ price(params), waking, lastCached }`
- ✅ Local caching keyed by stable hash of params
- ✅ User-initiated warm ping on app mount
- ✅ Progressive banner with escalating messages
- ✅ Cancel button to abort in-flight requests

## File Changes

### Backend Files
- `backend/app/main.py` - Updated with new `/health` and `/price` endpoints
- `backend/Procfile` - Updated for Render deployment
- `backend/render.yaml` - New infrastructure-as-code file

### Frontend Files
- `frontend/lib/hash.ts` - Deterministic param hash utility
- `frontend/lib/api.ts` - New API wrapper with cold-start handling
- `frontend/hooks/usePrice.ts` - Hook for price calculation with caching
- `frontend/components/WakeBanner.tsx` - Progressive wake banner component
- `frontend/app/page.tsx` - Updated to use new cold-start system

## Environment Setup

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_BASE=https://your-render-service.onrender.com
```

### Backend Environment Variables
- `PORT` - Automatically set by Render
- No additional environment variables required

## Usage

The system automatically handles cold starts transparently:

1. **First Request**: Shows "Waking server..." banner after 1.2s
2. **Progressive Messages**: 
   - 15s: "Still waking… Render Free can take ~30–60s on the first hit"
   - 45s: "Almost there… you can Cancel and retry anytime"
3. **Caching**: Shows last cached result while server wakes
4. **Retry Logic**: Up to 3 attempts with exponential backoff
5. **Cancellation**: Users can cancel requests at any time

## API Endpoints

### New Endpoints
- `GET /health` - Lightweight health check
- `POST /price` - Black-Scholes pricing with idempotency

### Existing Endpoints (Preserved)
- All existing `/api/*` endpoints remain unchanged for backward compatibility

## Deployment

### Render
1. Connect your GitHub repository to Render
2. Use the provided `render.yaml` for automatic deployment
3. Health check path: `/health`

### Local Development
```bash
# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
npm run dev
```

## Technical Details

### Idempotency
- Uses in-memory cache keyed by `idempotencyKey`
- Process-local (suitable for personal projects)
- For scaling, consider Redis/Postgres

### Caching Strategy
- Client-side caching by parameter hash
- Shows last successful result while server wakes
- Preserves user experience during cold starts

### Error Handling
- Graceful degradation during cold starts
- Clear error messages for users
- Automatic retry with exponential backoff

## Performance Characteristics

- **Cold Start**: ~30-60s on Render Free tier
- **Warm Start**: <1s response time
- **Health Check**: <100ms response time
- **Retry Strategy**: 3 attempts with 0.8s, 1.6s, 3.2s backoff
- **Timeout**: 30s per attempt to ride out cold starts
