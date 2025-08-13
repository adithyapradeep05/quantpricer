"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DollarSign, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface PriceCardProps {
  price: number | null;
  optionType: 'call' | 'put';
  loading: boolean;
  error?: string;
}

export default function PriceCard({ price, optionType, loading, error }: PriceCardProps) {
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
          <DollarSign className="w-5 h-5" />
          OPTION PRICE
        </CardTitle>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert className="bg-red-900/20 border-red-500 mb-4">
            <AlertCircle className="h-4 w-4 text-red-400" />
            <AlertDescription className="text-red-400 text-xs font-mono">
              {error}
            </AlertDescription>
          </Alert>
        )}
        
        <div className="text-center">
          <div className="text-gray-400 text-xs mb-2 font-mono tracking-wide">
            {optionType.toUpperCase()} OPTION PRICE
          </div>
          <div className="text-3xl font-bold text-green-400 font-mono">
            {loading ? (
              <div className="animate-pulse bg-gray-800 h-8 w-32 mx-auto rounded"></div>
            ) : error ? (
              <span className="text-red-400 text-lg">ERROR</span>
            ) : price !== null ? (
              `$${formatPrice(price)}`
            ) : (
              <span className="text-gray-500 text-lg">NO DATA</span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}