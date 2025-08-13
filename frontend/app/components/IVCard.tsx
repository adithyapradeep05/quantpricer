"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface IVCardProps {
  impliedVol: number | null;
  pricedWithIV: number | null;
  loading: boolean;
  error?: string;
}

export default function IVCard({ impliedVol, pricedWithIV, loading, error }: IVCardProps) {
  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 4,
      maximumFractionDigits: 4,
    }).format(price);
  };

  return (
    <Card className="bg-black border-gray-600 border-2">
      <CardHeader className="pb-3">
        <CardTitle className="text-green-400 flex items-center gap-2 font-mono text-sm tracking-wide">
          <TrendingUp className="w-5 h-5" />
          IMPLIED VOLATILITY
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <Alert className="bg-red-900/20 border-red-500">
            <AlertCircle className="h-4 w-4 text-red-400" />
            <AlertDescription className="text-red-400 text-xs font-mono">
              {error}
            </AlertDescription>
          </Alert>
        )}
        
        <div className="text-center">
          <div className="text-gray-400 text-xs mb-2 font-mono tracking-wide">IMPLIED VOLATILITY</div>
          <div className="text-2xl font-bold text-yellow-400 font-mono">
            {loading ? (
              <div className="animate-pulse bg-gray-800 h-6 w-24 mx-auto rounded"></div>
            ) : error ? (
              <span className="text-red-400 text-lg">ERROR</span>
            ) : impliedVol !== null ? (
              `${impliedVol.toFixed(5)} (${formatPercent(impliedVol)})`
            ) : (
              <span className="text-gray-500 text-lg">NO DATA</span>
            )}
          </div>
        </div>
        
        <div className="text-center border-t border-gray-600 pt-4">
          <div className="text-gray-400 text-xs mb-2 font-mono tracking-wide">PRICE WITH IV</div>
          <div className="text-xl font-semibold text-yellow-400 font-mono">
            {loading ? (
              <div className="animate-pulse bg-gray-800 h-6 w-20 mx-auto rounded"></div>
            ) : error ? (
              <span className="text-red-400">ERROR</span>
            ) : pricedWithIV !== null ? (
              `$${formatPrice(pricedWithIV)}`
            ) : (
              <span className="text-gray-500">NO DATA</span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}