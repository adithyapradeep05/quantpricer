from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import (
    PriceRequest, PriceResponse,
    GreeksRequest, GreeksResponse,
    IVRequest, IVResponse,
    CurveRequest, CurveResponse,
    HeatmapRequest, HeatmapResponse,
    HealthResponse
)
from .deps import generate_S_range, generate_vol_range
from src.core.bs import black_scholes_price
from src.core.greeks import calculate_all_greeks
from src.core.iv import implied_vol_from_price
from .charts_api import router as charts_router

app = FastAPI(
    title="QuantPricer API",
    description="Option pricing API using Black-Scholes formulas",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include charts router
app.include_router(charts_router)


@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")


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
