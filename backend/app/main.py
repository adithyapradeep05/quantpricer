import os
import math
import threading
from typing import Dict, Any
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="QuantPricer API",
    description="Option pricing API using Black-Scholes formulas",
    version="1.0.0"
)

# CORS configuration - more secure for production
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Next.js dev server
    "http://localhost:3001",  # Alternative dev port
    "https://your-frontend-domain.com",  # Add your production domain here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

_engine_lock = threading.Lock()
_engine_ready = False

def get_engine():
    global _engine_ready
    with _engine_lock:
        if not _engine_ready:
            # Lazy heavy init happens here; keep this minimal.
            # If you need numpy/scipy, import here.
            # For demo purposes we only set a flag.
            _engine_ready = True
    return True

# In-memory idempotency cache (process-local)
_IDEMP_CACHE: Dict[str, Dict[str, Any]] = {}

def _N(x: float) -> float:
    # Standard normal CDF via error function (no heavy deps)
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def _n(x: float) -> float:
    return math.exp(-0.5*x*x) / math.sqrt(2.0*math.pi)

@app.post("/price")
def price(payload: Dict[str, Any] = Body(...)):
    try:
        key = payload.get("idempotencyKey")
        if key and key in _IDEMP_CACHE:
            return _IDEMP_CACHE[key]

        get_engine()  # ensure lazy init

        S = float(payload["S"])
        K = float(payload["K"])
        r = float(payload["r"])
        q = float(payload.get("q", 0.0))
        sigma = float(payload["sigma"])
        T = float(payload["T"])
        typ = str(payload["type"]).lower()  # "call" or "put"

        if sigma <= 0 or S <= 0 or K <= 0 or T <= 0:
            raise ValueError("Invalid inputs")

        d1 = (math.log(S/K) + (r - q + 0.5*sigma*sigma)*T) / (sigma*math.sqrt(T))
        d2 = d1 - sigma*math.sqrt(T)
        df_r = math.exp(-r*T)
        df_q = math.exp(-q*T)

        if typ == "call":
            px = S*df_q*_N(d1) - K*df_r*_N(d2)
            delta = df_q*_N(d1)
            rho = K*T*df_r*_N(d2)
            theta = (-(S*df_q*_n(d1)*sigma)/(2*math.sqrt(T))) + q*S*df_q*_N(-d1) - r*K*df_r*_N(d2)
        elif typ == "put":
            px = K*df_r*_N(-d2) - S*df_q*_N(-d1)
            delta = -df_q*_N(-d1)
            rho = -K*T*df_r*_N(-d2)
            theta = (-(S*df_q*_n(d1)*sigma)/(2*math.sqrt(T))) + q*S*df_q*_N(d1) + r*K*df_r*_N(-d2)
        else:
            raise ValueError("type must be 'call' or 'put'")

        gamma = df_q*_n(d1)/(S*sigma*math.sqrt(T))
        vega  = S*df_q*_n(d1)*math.sqrt(T)      # per 1.0 vol
        greeks = {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho}

        resp = {
            "price": px,
            "greeks": greeks,
            "meta": {"engine": "lazy-bs", "ok": True}
        }

        if key:
            _IDEMP_CACHE[key] = resp
        return resp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Keep existing endpoints for backward compatibility
@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

# New cold-start optimized price endpoint
@app.post("/price")
def price(payload: Dict[str, Any] = Body(...)):
    try:
        key = payload.get("idempotencyKey")
        if key and key in _IDEMP_CACHE:
            return _IDEMP_CACHE[key]

        get_engine()  # ensure lazy init

        S = float(payload["S"])
        K = float(payload["K"])
        r = float(payload["r"])
        q = float(payload.get("q", 0.0))
        sigma = float(payload["sigma"])
        T = float(payload["T"])
        typ = str(payload["type"]).lower()  # "call" or "put"

        if sigma <= 0 or S <= 0 or K <= 0 or T <= 0:
            raise ValueError("Invalid inputs")

        d1 = (math.log(S/K) + (r - q + 0.5*sigma*sigma)*T) / (sigma*math.sqrt(T))
        d2 = d1 - sigma*math.sqrt(T)
        df_r = math.exp(-r*T)
        df_q = math.exp(-q*T)

        if typ == "call":
            px = S*df_q*_N(d1) - K*df_r*_N(d2)
            delta = df_q*_N(d1)
            rho = K*T*df_r*_N(d2)
            theta = (-(S*df_q*_n(d1)*sigma)/(2*math.sqrt(T))) + q*S*df_q*_N(-d1) - r*K*df_r*_N(d2)
        elif typ == "put":
            px = K*df_r*_N(-d2) - S*df_q*_N(-d1)
            delta = -df_q*_N(-d1)
            rho = -K*T*df_r*_N(-d2)
            theta = (-(S*df_q*_n(d1)*sigma)/(2*math.sqrt(T))) + q*S*df_q*_N(d1) + r*K*df_r*_N(-d2)
        else:
            raise ValueError("type must be 'call' or 'put'")

        gamma = df_q*_n(d1)/(S*sigma*math.sqrt(T))
        vega  = S*df_q*_n(d1)*math.sqrt(T)      # per 1.0 vol
        greeks = {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho}

        resp = {
            "price": px,
            "greeks": greeks,
            "meta": {"engine": "lazy-bs", "ok": True}
        }

        if key:
            _IDEMP_CACHE[key] = resp
        return resp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Include existing routers and endpoints
from .charts_api import router as charts_router
app.include_router(charts_router)

# Import and add existing endpoints
from .schemas import (
    PriceRequest, PriceResponse,
    GreeksRequest, GreeksResponse,
    IVRequest, IVResponse,
    CurveRequest, CurveResponse,
    HeatmapRequest, HeatmapResponse,
    HealthResponse,
    GreeksCurveRequest, GreeksCurveResponse
)
from .deps import generate_S_range, generate_vol_range
from src.core.bs import black_scholes_price
from src.core.greeks import calculate_all_greeks
from src.core.iv import implied_vol_from_price

@app.post("/api/price", response_model=PriceResponse)
async def calculate_price(request: PriceRequest):
    try:
        price = black_scholes_price(
            S=request.S,
            K=request.K,
            T=request.T,
            r=request.r,
            sigma=request.sigma,
            option_type=request.option_type
        )
        return PriceResponse(price=price)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/greeks", response_model=GreeksResponse)
async def calculate_greeks(request: GreeksRequest):
    try:
        greeks = calculate_all_greeks(
            S=request.S,
            K=request.K,
            T=request.T,
            r=request.r,
            sigma=request.sigma,
            option_type=request.option_type
        )
        return GreeksResponse(**greeks)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/implied-vol", response_model=IVResponse)
async def calculate_implied_volatility(request: IVRequest):
    try:
        is_call = request.option_type == "call"
        implied_vol = implied_vol_from_price(
            price=request.market_price,
            S=request.S,
            K=request.K,
            r=request.r,
            T=request.T,
            is_call=is_call
        )
        
        priced_with_iv = black_scholes_price(
            S=request.S,
            K=request.K,
            T=request.T,
            r=request.r,
            sigma=implied_vol,
            option_type=request.option_type
        )
        
        return IVResponse(
            implied_vol=implied_vol,
            priced_with_iv=priced_with_iv
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/curve", response_model=CurveResponse)
async def generate_price_curve(request: CurveRequest):
    try:
        prices = []
        for S in request.S_values:
            price = black_scholes_price(
                S=S,
                K=request.K,
                T=request.T,
                r=request.r,
                sigma=request.sigma,
                option_type=request.option_type
            )
            prices.append(price)
        
        return CurveResponse(
            S_values=request.S_values,
            prices=prices
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/heatmap", response_model=HeatmapResponse)
async def generate_price_heatmap(request: HeatmapRequest):
    try:
        z = []
        for vol in request.vol_values:
            row = []
            for S in request.S_values:
                price = black_scholes_price(
                    S=S,
                    K=request.K,
                    T=request.T,
                    r=request.r,
                    sigma=vol,
                    option_type=request.option_type
                )
                row.append(price)
            z.append(row)
        
        return HeatmapResponse(
            z=z,
            S_values=request.S_values,
            vol_values=request.vol_values
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/api/curve/default", response_model=CurveResponse)
async def get_default_curve(
    K: float = 100,
    r: float = 0.05,
    sigma: float = 0.2,
    T: float = 1.0,
    option_type: str = "call"
):
    try:
        S_values = generate_S_range(K)
        prices = []
        for S in S_values:
            price = black_scholes_price(
                S=S,
                K=K,
                T=T,
                r=r,
                sigma=sigma,
                option_type=option_type
            )
            prices.append(price)
        
        return CurveResponse(
            S_values=S_values,
            prices=prices
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/api/heatmap/default", response_model=HeatmapResponse)
async def get_default_heatmap(
    K: float = 100,
    r: float = 0.05,
    T: float = 1.0,
    option_type: str = "call"
):
    try:
        S_values = generate_S_range(K)
        vol_values = generate_vol_range()
        
        z = []
        for vol in vol_values:
            row = []
            for S in S_values:
                price = black_scholes_price(
                    S=S,
                    K=K,
                    T=T,
                    r=r,
                    sigma=vol,
                    option_type=option_type
                )
                row.append(price)
            z.append(row)
        
        return HeatmapResponse(
            z=z,
            S_values=S_values,
            vol_values=vol_values
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/greeks-curves", response_model=GreeksCurveResponse)
async def generate_greeks_curves(request: GreeksCurveRequest):
    try:
        delta_values = []
        gamma_values = []
        vega_values = []
        theta_values = []
        rho_values = []
        
        for S in request.S_values:
            greeks = calculate_all_greeks(
                S=S,
                K=request.K,
                T=request.T,
                r=request.r,
                sigma=request.sigma,
                option_type=request.option_type
            )
            delta_values.append(greeks['delta'])
            gamma_values.append(greeks['gamma'])
            vega_values.append(greeks['vega'])
            theta_values.append(greeks['theta'])
            rho_values.append(greeks['rho'])
        
        return GreeksCurveResponse(
            S_values=request.S_values,
            delta=delta_values,
            gamma=gamma_values,
            vega=vega_values,
            theta=theta_values,
            rho=rho_values
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
