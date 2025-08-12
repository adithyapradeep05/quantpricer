"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calculator, Loader2 } from 'lucide-react';

interface ControlsProps {
  onCalculate: (params: any) => void;
  loading: boolean;
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

  const handleInputChange = (field: string, value: string | number) => {
    setParams(prev => ({
      ...prev,
      [field]: typeof value === 'string' && field !== 'option_type' ? parseFloat(value) || 0 : value
    }));
  };

  const handleCalculate = () => {
    onCalculate(params);
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
          disabled={loading}
          className="w-full bg-green-600 hover:bg-green-700 text-black font-bold py-3 font-mono tracking-wide border border-green-500"
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
                value={params.S}
                onChange={(e) => handleInputChange('S', e.target.value)}
                className="bg-gray-900 border-gray-500 text-green-400 mt-1 font-mono"
              />
            </div>
            <div>
              <Label htmlFor="K" className="text-gray-300 text-xs font-mono tracking-wide">
                STRIKE PRICE (K)
              </Label>
              <Input
                id="K"
                type="number"
                step="0.01"
                value={params.K}
                onChange={(e) => handleInputChange('K', e.target.value)}
                className="bg-gray-900 border-gray-500 text-green-400 mt-1 font-mono"
              />
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
                value={params.r}
                onChange={(e) => handleInputChange('r', e.target.value)}
                className="bg-gray-900 border-gray-500 text-green-400 mt-1 font-mono"
              />
            </div>
            <div>
              <Label htmlFor="T" className="text-gray-300 text-xs font-mono tracking-wide">
                TIME TO EXPIRY (T)
              </Label>
              <Input
                id="T"
                type="number"
                step="0.01"
                value={params.T}
                onChange={(e) => handleInputChange('T', e.target.value)}
                className="bg-gray-900 border-gray-500 text-green-400 mt-1 font-mono"
              />
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
              value={params.sigma}
              onChange={(e) => handleInputChange('sigma', e.target.value)}
              className="bg-gray-900 border-gray-500 text-green-400 mt-1 font-mono"
            />
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
              value={params.market_price}
              onChange={(e) => handleInputChange('market_price', e.target.value)}
              className="bg-gray-900 border-gray-500 text-green-400 mt-1 font-mono"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
