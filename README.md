# QuantPricer

A professional option pricing tool built with Next.js 14 and FastAPI, featuring real-time Black-Scholes calculations, Greeks analysis, and interactive charts.

## Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **TailwindCSS**
- **shadcn/ui** components
- **HTML Canvas** for charts
- **Axios** for API calls

### Backend
- **FastAPI** (Python 3.11)
- **Pydantic** for data validation
- **NumPy** for numerical computations
- **Custom Black-Scholes implementation** (no SciPy dependency)

## Features

- **Option Pricing**: Black-Scholes call/put calculations
- **Greeks Analysis**: Delta, Gamma, Vega, Theta, Rho
- **Implied Volatility**: Bisection + Newton-Raphson methods
- **Interactive Charts**: Price curves and volatility heatmaps
- **Real-time Updates**: Instant calculations with professional UI

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd quantpricer
   ```

2. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open your browser**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Endpoints

- `POST /api/price` - Calculate option price
- `POST /api/greeks` - Calculate option Greeks
- `POST /api/implied-vol` - Calculate implied volatility
- `POST /api/curve` - Generate price curve data
- `POST /api/heatmap` - Generate volatility heatmap data
- `GET /healthz` - Health check

## Project Structure

```
quantpricer/
├── frontend/                 # Next.js application
│   ├── app/                 # App Router pages
│   ├── components/          # React components
│   └── package.json
├── backend/                 # FastAPI application
│   ├── app/                # API routes and schemas
│   ├── src/core/           # Core math modules
│   └── requirements.txt
└── README.md
```

## Development

- **Frontend**: `npm run dev` (runs on port 3000)
- **Backend**: `uvicorn app.main:app --reload` (runs on port 8000)
- **Build**: `npm run build` (frontend)
- **Lint**: `npm run lint` (frontend)

## Deployment

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set root directory to `frontend`
3. Add environment variable: `NEXT_PUBLIC_API_URL` = your backend URL
4. Deploy

### Backend (Render/Railway)
1. Deploy to Render or Railway
2. Set source directory to `backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Environment Variables

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL (e.g., `https://your-app.onrender.com`)

### Backend
- `PORT`: Port number (auto-set by platform)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License


