"""
Pydantic schemas for QuantPricer API.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Literal

OptionType = Literal["call", "put"]


class PriceRequest(BaseModel):
    S: float = Field(..., gt=0, le=10000, description="Stock price")
    K: float = Field(..., gt=0, le=10000, description="Strike price")
    r: float = Field(..., ge=-0.5, le=2, description="Risk-free rate")
    T: float = Field(..., ge=0, le=50, description="Time to expiration (years)")
    sigma: float = Field(..., ge=0, le=5, description="Volatility")
    option_type: OptionType = Field(..., description="Option type: call or put")

    @validator('S', 'K')
    def validate_prices(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        if v > 10000:
            raise ValueError('Price too high (max: 10,000)')
        return v

    @validator('r')
    def validate_rate(cls, v):
        if v < -0.5:
            raise ValueError('Risk-free rate too low (min: -50%)')
        if v > 2:
            raise ValueError('Risk-free rate too high (max: 200%)')
        return v

    @validator('T')
    def validate_time(cls, v):
        if v < 0:
            raise ValueError('Time to expiry must be non-negative')
        if v > 50:
            raise ValueError('Time to expiry too long (max: 50 years)')
        return v

    @validator('sigma')
    def validate_volatility(cls, v):
        if v < 0:
            raise ValueError('Volatility must be non-negative')
        if v > 5:
            raise ValueError('Volatility too high (max: 500%)')
        return v


class PriceResponse(BaseModel):
    price: float = Field(..., description="Option price")


class GreeksRequest(BaseModel):
    S: float = Field(..., gt=0, le=10000, description="Stock price")
    K: float = Field(..., gt=0, le=10000, description="Strike price")
    r: float = Field(..., ge=-0.5, le=2, description="Risk-free rate")
    T: float = Field(..., ge=0, le=50, description="Time to expiration (years)")
    sigma: float = Field(..., ge=0, le=5, description="Volatility")
    option_type: OptionType = Field(..., description="Option type: call or put")

    @validator('S', 'K')
    def validate_prices(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        if v > 10000:
            raise ValueError('Price too high (max: 10,000)')
        return v

    @validator('r')
    def validate_rate(cls, v):
        if v < -0.5:
            raise ValueError('Risk-free rate too low (min: -50%)')
        if v > 2:
            raise ValueError('Risk-free rate too high (max: 200%)')
        return v

    @validator('T')
    def validate_time(cls, v):
        if v < 0:
            raise ValueError('Time to expiry must be non-negative')
        if v > 50:
            raise ValueError('Time to expiry too long (max: 50 years)')
        return v

    @validator('sigma')
    def validate_volatility(cls, v):
        if v < 0:
            raise ValueError('Volatility must be non-negative')
        if v > 5:
            raise ValueError('Volatility too high (max: 500%)')
        return v


class GreeksResponse(BaseModel):
    delta: float = Field(..., description="Delta")
    gamma: float = Field(..., description="Gamma")
    vega: float = Field(..., description="Vega")
    theta: float = Field(..., description="Theta (annualized)")
    rho: float = Field(..., description="Rho")


class IVRequest(BaseModel):
    market_price: float = Field(..., ge=0, le=10000, description="Market price of the option")
    S: float = Field(..., gt=0, le=10000, description="Stock price")
    K: float = Field(..., gt=0, le=10000, description="Strike price")
    r: float = Field(..., ge=-0.5, le=2, description="Risk-free rate")
    T: float = Field(..., ge=0, le=50, description="Time to expiration (years)")
    option_type: OptionType = Field(..., description="Option type: call or put")

    @validator('market_price')
    def validate_market_price(cls, v):
        if v < 0:
            raise ValueError('Market price must be non-negative')
        if v > 10000:
            raise ValueError('Market price too high (max: 10,000)')
        return v

    @validator('S', 'K')
    def validate_prices(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        if v > 10000:
            raise ValueError('Price too high (max: 10,000)')
        return v

    @validator('r')
    def validate_rate(cls, v):
        if v < -0.5:
            raise ValueError('Risk-free rate too low (min: -50%)')
        if v > 2:
            raise ValueError('Risk-free rate too high (max: 200%)')
        return v

    @validator('T')
    def validate_time(cls, v):
        if v < 0:
            raise ValueError('Time to expiry must be non-negative')
        if v > 50:
            raise ValueError('Time to expiry too long (max: 50 years)')
        return v


class IVResponse(BaseModel):
    implied_vol: float = Field(..., description="Implied volatility")
    priced_with_iv: float = Field(..., description="Price calculated with implied volatility")


class CurveRequest(BaseModel):
    S_values: List[float] = Field(..., description="Stock price values")
    K: float = Field(..., gt=0, le=10000, description="Strike price")
    r: float = Field(..., ge=-0.5, le=2, description="Risk-free rate")
    sigma: float = Field(..., ge=0, le=5, description="Volatility")
    T: float = Field(..., ge=0, le=50, description="Time to expiration (years)")
    option_type: OptionType = Field(..., description="Option type: call or put")

    @validator('S_values')
    def validate_S_values(cls, v):
        if not v:
            raise ValueError('S_values cannot be empty')
        if len(v) > 1000:
            raise ValueError('Too many S_values (max: 1000)')
        if any(s <= 0 for s in v):
            raise ValueError('All S_values must be positive')
        if any(s > 10000 for s in v):
            raise ValueError('All S_values must be <= 10,000')
        return v

    @validator('K')
    def validate_strike(cls, v):
        if v <= 0:
            raise ValueError('Strike price must be positive')
        if v > 10000:
            raise ValueError('Strike price too high (max: 10,000)')
        return v

    @validator('r')
    def validate_rate(cls, v):
        if v < -0.5:
            raise ValueError('Risk-free rate too low (min: -50%)')
        if v > 2:
            raise ValueError('Risk-free rate too high (max: 200%)')
        return v

    @validator('sigma')
    def validate_volatility(cls, v):
        if v < 0:
            raise ValueError('Volatility must be non-negative')
        if v > 5:
            raise ValueError('Volatility too high (max: 500%)')
        return v

    @validator('T')
    def validate_time(cls, v):
        if v < 0:
            raise ValueError('Time to expiry must be non-negative')
        if v > 50:
            raise ValueError('Time to expiry too long (max: 50 years)')
        return v


class CurveResponse(BaseModel):
    S_values: List[float] = Field(..., description="Stock price values")
    prices: List[float] = Field(..., description="Option prices")


class HeatmapRequest(BaseModel):
    S_values: List[float] = Field(..., description="Stock price values")
    vol_values: List[float] = Field(..., description="Volatility values")
    K: float = Field(..., gt=0, le=10000, description="Strike price")
    r: float = Field(..., ge=-0.5, le=2, description="Risk-free rate")
    T: float = Field(..., ge=0, le=50, description="Time to expiration (years)")
    option_type: OptionType = Field(..., description="Option type: call or put")

    @validator('S_values')
    def validate_S_values(cls, v):
        if not v:
            raise ValueError('S_values cannot be empty')
        if len(v) > 100:
            raise ValueError('Too many S_values (max: 100)')
        if any(s <= 0 for s in v):
            raise ValueError('All S_values must be positive')
        if any(s > 10000 for s in v):
            raise ValueError('All S_values must be <= 10,000')
        return v

    @validator('vol_values')
    def validate_vol_values(cls, v):
        if not v:
            raise ValueError('vol_values cannot be empty')
        if len(v) > 100:
            raise ValueError('Too many vol_values (max: 100)')
        if any(vol < 0 for vol in v):
            raise ValueError('All vol_values must be non-negative')
        if any(vol > 5 for vol in v):
            raise ValueError('All vol_values must be <= 500%')
        return v

    @validator('K')
    def validate_strike(cls, v):
        if v <= 0:
            raise ValueError('Strike price must be positive')
        if v > 10000:
            raise ValueError('Strike price too high (max: 10,000)')
        return v

    @validator('r')
    def validate_rate(cls, v):
        if v < -0.5:
            raise ValueError('Risk-free rate too low (min: -50%)')
        if v > 2:
            raise ValueError('Risk-free rate too high (max: 200%)')
        return v

    @validator('T')
    def validate_time(cls, v):
        if v < 0:
            raise ValueError('Time to expiry must be non-negative')
        if v > 50:
            raise ValueError('Time to expiry too long (max: 50 years)')
        return v


class HeatmapResponse(BaseModel):
    z: List[List[float]] = Field(..., description="2D array of prices [vol_values][S_values]")
    S_values: List[float] = Field(..., description="Stock price values")
    vol_values: List[float] = Field(..., description="Volatility values")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
