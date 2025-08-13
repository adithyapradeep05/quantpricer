"""
Charts API endpoints for QuantPricer.
Generates JSON data for frontend chart rendering.
"""

from fastapi import APIRouter, HTTPException
from .schemas import (
    CurveRequest, CurveResponse,
    HeatmapRequest, HeatmapResponse,
    GreeksCurveRequest, GreeksCurveResponse
)
from src.core.bs import black_scholes_price
from src.core.greeks import calculate_all_greeks

router = APIRouter()


@router.post("/api/curve", response_model=CurveResponse)
async def generate_price_curve(request: CurveRequest):
    """
    Generate price curve data for plotting option prices vs stock prices.
    
    Args:
        request: CurveRequest with S_values, K, r, sigma, T, option_type
        
    Returns:
        CurveResponse with S_values and corresponding prices
    """
    try:
        prices = []
        for S in request.S_values:
            try:
                price = black_scholes_price(
                    S=S,
                    K=request.K,
                    T=request.T,
                    r=request.r,
                    sigma=request.sigma,
                    option_type=request.option_type
                )
                prices.append(price)
            except ValueError as e:
                # If individual calculation fails, use NaN or skip
                prices.append(float('nan'))
        
        return CurveResponse(
            S_values=request.S_values,
            prices=prices
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error generating price curve: {str(e)}")


@router.post("/api/heatmap", response_model=HeatmapResponse)
async def generate_price_heatmap(request: HeatmapRequest):
    """
    Generate heatmap data for plotting option prices vs stock prices and volatility.
    
    Args:
        request: HeatmapRequest with S_values, vol_values, K, r, T, option_type
        
    Returns:
        HeatmapResponse with 2D array of prices [vol_values][S_values]
    """
    try:
        z = []
        for vol in request.vol_values:
            row = []
            for S in request.S_values:
                try:
                    price = black_scholes_price(
                        S=S,
                        K=request.K,
                        T=request.T,
                        r=request.r,
                        sigma=vol,
                        option_type=request.option_type
                    )
                    row.append(price)
                except ValueError:
                    # If individual calculation fails, use NaN
                    row.append(float('nan'))
            z.append(row)
        
        return HeatmapResponse(
            z=z,
            S_values=request.S_values,
            vol_values=request.vol_values
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error generating heatmap: {str(e)}")


@router.post("/api/greeks-curves", response_model=GreeksCurveResponse)
async def generate_greeks_curves(request: GreeksCurveRequest):
    """
    Generate Greeks curves data for plotting all Greeks vs stock prices.
    
    Args:
        request: GreeksCurveRequest with S_values, K, r, sigma, T, option_type
        
    Returns:
        GreeksCurveResponse with S_values and corresponding Greeks values
    """
    try:
        deltas, gammas, vegas, thetas, rhos = [], [], [], [], []
        
        for S in request.S_values:
            try:
                greeks = calculate_all_greeks(
                    S=S,
                    K=request.K,
                    T=request.T,
                    r=request.r,
                    sigma=request.sigma,
                    option_type=request.option_type
                )
                deltas.append(greeks['delta'])
                gammas.append(greeks['gamma'])
                vegas.append(greeks['vega'])
                thetas.append(greeks['theta'])
                rhos.append(greeks['rho'])
            except ValueError:
                # If individual calculation fails, use NaN
                deltas.append(float('nan'))
                gammas.append(float('nan'))
                vegas.append(float('nan'))
                thetas.append(float('nan'))
                rhos.append(float('nan'))
        
        return GreeksCurveResponse(
            S_values=request.S_values,
            delta=deltas,
            gamma=gammas,
            vega=vegas,
            theta=thetas,
            rho=rhos
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error generating Greeks curves: {str(e)}")
