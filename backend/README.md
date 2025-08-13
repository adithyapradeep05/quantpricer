# QuantPricer Backend

FastAPI backend for option pricing using Black-Scholes formulas.

## Features

- Option pricing using Black-Scholes model
- Greeks calculation (Delta, Gamma, Vega, Theta, Rho)
- Implied volatility calculation
- Price curves and heatmaps
- RESTful API with automatic documentation

## Installation

```bash
pip install -r requirements.txt
```

## Development

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

- `POST /api/price` - Calculate option price
- `POST /api/greeks` - Calculate option Greeks
- `POST /api/implied-vol` - Calculate implied volatility
- `POST /api/curve` - Generate price curve
- `POST /api/heatmap` - Generate price heatmap
- `GET /healthz` - Health check

## Deployment

### Render

1. Connect your repository to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. Set environment variable: `PORT=8000`

### Railway

1. Connect your repository to Railway
2. Railway will automatically detect the Python app
3. Set environment variable: `PORT=8000`

### Docker

```bash
docker build -t quantpricer-backend .
docker run -p 8000:8000 quantpricer-backend
```

## CORS Configuration

The API is configured to allow CORS from all origins for development. For production, update the `allow_origins` in `app/main.py` to include only your frontend domain.
