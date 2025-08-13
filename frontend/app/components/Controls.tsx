"use client";

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calculator, Loader2, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface ControlsProps {
  onCalculate: (params: any) => void;
  loading: boolean;
}

interface ValidationErrors {
  S?: string;
  K?: string;
  r?: string;
  T?: string;
  sigma?: string;
  market_price?: string;
}

export default function Controls({ onCalculate, loading }: ControlsProps) {
  const [params, setParams] = useState({
    S: 100,
    K: 100,
    r: 0.05,
    T: 1,
    sigma: 0.2,
    option_type: 'call' as 'call' | 'put',
    market_price: 10,
  });

  const [errors, setErrors] = useState<ValidationErrors>({});
  const [isValid, setIsValid] = useState(true);

  const validateInputs = (values: typeof params): ValidationErrors => {
    const newErrors: ValidationErrors = {};

    // Stock Price validation
    if (values.S <= 0) {
      newErrors.S = "Stock price must be positive";
    } else if (values.S > 10000) {
      newErrors.S = "Stock price too high (max: 10,000)";
    }

    // Strike Price validation
    if (values.K <= 0) {
      newErrors.K = "Strike price must be positive";
    } else if (values.K > 10000) {
      newErrors.K = "Strike price too high (max: 10,000)";
    }

    // Risk-free rate validation
    if (values.r < -0.5) {
      newErrors.r = "Risk-free rate too low (min: -50%)";
    } else if (values.r > 2) {
      newErrors.r = "Risk-free rate too high (max: 200%)";
    }

    // Time to expiry validation
    if (values.T < 0) {
      newErrors.T = "Time to expiry must be non-negative";
    } else if (values.T > 50) {
      newErrors.T = "Time to expiry too long (max: 50 years)";
    }

    // Volatility validation
    if (values.sigma < 0) {
      newErrors.sigma = "Volatility must be non-negative";
    } else if (values.sigma > 5) {
      newErrors.sigma = "Volatility too high (max: 500%)";
    }

    // Market price validation
    if (values.market_price < 0) {
      newErrors.market_price = "Market price must be non-negative";
    } else if (values.market_price > 10000) {
      newErrors.market_price = "Market price too high (max: 10,000)";
    }

    // Check for no-arbitrage bounds for implied volatility
    if (!newErrors.S && !newErrors.K && !newErrors.r && !newErrors.T && !newErrors.market_price) {
      const S = values.S;
      const K = values.K;
      const r = values.r;
      const T = values.T;
      const market_price = values.market_price;

      if (T > 0) {
        if (values.option_type === 'call') {
          const upper_bound = S;
          const lower_bound = Math.max(0, S - K * Math.exp(-r * T));
          
          if (market_price > upper_bound) {
            newErrors.market_price = `Price exceeds upper bound (${upper_bound.toFixed(2)})`;
          } else if (market_price < lower_bound) {
            newErrors.market_price = `Price below lower bound (${lower_bound.toFixed(2)})`;
          }
        } else {
          const upper_bound = K * Math.exp(-r * T);
          const lower_bound = Math.max(0, K * Math.exp(-r * T) - S);
          
          if (market_price > upper_bound) {
            newErrors.market_price = `Price exceeds upper bound (${upper_bound.toFixed(2)})`;
          } else if (market_price < lower_bound) {
            newErrors.market_price = `Price below lower bound (${lower_bound.toFixed(2)})`;
          }
        }
      } else if (T === 0) {
        // At expiration
        if (values.option_type === 'call') {
          const intrinsic = Math.max(0, S - K);
          if (Math.abs(market_price - intrinsic) > 0.01) {
            newErrors.market_price = `At expiration, price should be ${intrinsic.toFixed(2)}`;
          }
        } else {
          const intrinsic = Math.max(0, K - S);
          if (Math.abs(market_price - intrinsic) > 0.01) {
            newErrors.market_price = `At expiration, price should be ${intrinsic.toFixed(2)}`;
          }
        }
      }
    }

    return newErrors;
  };

  useEffect(() => {
    const newErrors = validateInputs(params);
    setErrors(newErrors);
    setIsValid(Object.keys(newErrors).length === 0);
  }, [params]);

  const handleInputChange = (field: string, value: string | number) => {
    const newValue = typeof value === 'string' && field !== 'option_type' ? parseFloat(value) || 0 : value;
    setParams(prev => ({
      ...prev,
      [field]: newValue
    }));
  };

  const handleCalculate = () => {
    if (isValid) {
      onCalculate(params);
    }
  };

  const getInputClassName = (field: keyof ValidationErrors) => {
    const baseClass = "bg-gray-900 border-gray-500 text-green-400 mt-1 font-mono";
    return errors[field] 
      ? `${baseClass} border-red-500 focus:border-red-400` 
      : `${baseClass} focus:border-green-400`;
  };

  return (
    <Card className="bg-black border-gray-600 border-2">
      <CardHeader className="pb-4">
        <CardTitle className="text-green-400 flex items-center gap-2 font-mono text-sm tracking-wide">
          <Calculator className="w-5 h-5" />
          OPTION PARAMETERS
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <Button
          onClick={handleCalculate}
          disabled={loading || !isValid}
          className="w-full bg-green-600 hover:bg-green-700 text-black font-bold py-3 font-mono tracking-wide border border-green-500 disabled:bg-gray-700 disabled:text-gray-400"
          size="lg"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              CALCULATING...
            </>
          ) : (
            <>
              <Calculator className="w-4 h-4 mr-2" />
              CALCULATE OPTION PRICE
            </>
          )}
        </Button>

        {!isValid && (
          <Alert className="bg-red-900/20 border-red-500">
            <AlertCircle className="h-4 w-4 text-red-400" />
            <AlertDescription className="text-red-400 text-xs font-mono">
              Please fix validation errors before calculating
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="S" className="text-gray-300 text-xs font-mono tracking-wide">
                STOCK PRICE (S)
              </Label>
              <Input
                id="S"
                type="number"
                step="0.01"
                min="0.01"
                max="10000"
                value={params.S}
                onChange={(e) => handleInputChange('S', e.target.value)}
                className={getInputClassName('S')}
              />
              {errors.S && (
                <p className="text-red-400 text-xs mt-1 font-mono">{errors.S}</p>
              )}
            </div>
            <div>
              <Label htmlFor="K" className="text-gray-300 text-xs font-mono tracking-wide">
                STRIKE PRICE (K)
              </Label>
              <Input
                id="K"
                type="number"
                step="0.01"
                min="0.01"
                max="10000"
                value={params.K}
                onChange={(e) => handleInputChange('K', e.target.value)}
                className={getInputClassName('K')}
              />
              {errors.K && (
                <p className="text-red-400 text-xs mt-1 font-mono">{errors.K}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="r" className="text-gray-300 text-xs font-mono tracking-wide">
                RISK-FREE RATE (r)
              </Label>
              <Input
                id="r"
                type="number"
                step="0.001"
                min="-0.5"
                max="2"
                value={params.r}
                onChange={(e) => handleInputChange('r', e.target.value)}
                className={getInputClassName('r')}
              />
              {errors.r && (
                <p className="text-red-400 text-xs mt-1 font-mono">{errors.r}</p>
              )}
            </div>
            <div>
              <Label htmlFor="T" className="text-gray-300 text-xs font-mono tracking-wide">
                TIME TO EXPIRY (T)
              </Label>
              <Input
                id="T"
                type="number"
                step="0.01"
                min="0"
                max="50"
                value={params.T}
                onChange={(e) => handleInputChange('T', e.target.value)}
                className={getInputClassName('T')}
              />
              {errors.T && (
                <p className="text-red-400 text-xs mt-1 font-mono">{errors.T}</p>
              )}
            </div>
          </div>

          <div>
            <Label htmlFor="sigma" className="text-gray-300 text-xs font-mono tracking-wide">
              VOLATILITY (σ)
            </Label>
            <Input
              id="sigma"
              type="number"
              step="0.001"
              min="0"
              max="5"
              value={params.sigma}
              onChange={(e) => handleInputChange('sigma', e.target.value)}
              className={getInputClassName('sigma')}
            />
            {errors.sigma && (
              <p className="text-red-400 text-xs mt-1 font-mono">{errors.sigma}</p>
            )}
          </div>

          <div>
            <Label htmlFor="option_type" className="text-gray-300 text-xs font-mono tracking-wide">
              OPTION TYPE
            </Label>
            <Select
              value={params.option_type}
              onValueChange={(value: 'call' | 'put') => handleInputChange('option_type', value)}
            >
              <SelectTrigger className="bg-gray-900 border-gray-500 text-green-400 mt-1 font-mono">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-gray-900 border-gray-500">
                <SelectItem value="call" className="text-green-400 hover:bg-gray-800 font-mono">CALL</SelectItem>
                <SelectItem value="put" className="text-red-400 hover:bg-gray-800 font-mono">PUT</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="market_price" className="text-gray-300 text-xs font-mono tracking-wide">
              MARKET PRICE (FOR IV)
            </Label>
            <Input
              id="market_price"
              type="number"
              step="0.01"
              min="0"
              max="10000"
              value={params.market_price}
              onChange={(e) => handleInputChange('market_price', e.target.value)}
              className={getInputClassName('market_price')}
            />
            {errors.market_price && (
              <p className="text-red-400 text-xs mt-1 font-mono">{errors.market_price}</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
