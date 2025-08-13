"use client";

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { api, linspace } from '../../api-client';

interface PriceCurveProps {
  optionType: 'call' | 'put';
  K: number;
  r: number;
  sigma: number;
  T: number;
  Smin?: number;
  Smax?: number;
  points?: number;
  error?: string;
}

export default function PriceCurve({ 
  optionType, 
  K, 
  r, 
  sigma, 
  T, 
  Smin, 
  Smax, 
  points = 201,
  error: propError 
}: PriceCurveProps) {
  const [data, setData] = useState<{ S_values: number[], prices: number[] } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(propError || null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const defaultSmin = Smin || 0.5 * K;
  const defaultSmax = Smax || 1.5 * K;

  useEffect(() => {
    setError(propError || null);
  }, [propError]);

  useEffect(() => {
    const fetchData = async () => {
      if (!K || !r || !sigma || !T) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const S_values = linspace(defaultSmin, defaultSmax, points);
        
        const response = await api.postCurve({
          S_values,
          K,
          r,
          sigma,
          T,
          option_type: optionType,
        });

        setData({
          S_values: response.S_values,
          prices: response.prices
        });
             } catch (err: any) {
         console.error('Error fetching price curve data:', err);
         const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch price curve data';
         setError(typeof errorMessage === 'string' ? errorMessage : 'Failed to fetch price curve data');
       } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [optionType, K, r, sigma, T, defaultSmin, defaultSmax, points]);

  useEffect(() => {
    if (!data || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { S_values, prices } = data;
    
    // Set canvas size
    const width = canvas.offsetWidth;
    const height = canvas.offsetHeight;
    canvas.width = width;
    canvas.height = height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    if (S_values.length === 0) return;

         // Find min and max values for scaling
     const validPrices = prices.filter(p => !isNaN(p) && isFinite(p));
     if (validPrices.length === 0) return;
     
     const minS = Math.min(...S_values);
     const maxS = Math.max(...S_values);
     const minPrice = Math.min(...validPrices);
     const maxPrice = Math.max(...validPrices);

    // Draw grid
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);
    
    // Vertical grid lines
    for (let i = 0; i <= 5; i++) {
      const x = (width * i) / 5;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    
    // Horizontal grid lines
    for (let i = 0; i <= 5; i++) {
      const y = (height * i) / 5;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
    ctx.setLineDash([]);

    // Draw strike line
    const strikeX = ((K - minS) / (maxS - minS)) * width;
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 6]);
    ctx.beginPath();
    ctx.moveTo(strikeX, 0);
    ctx.lineTo(strikeX, height);
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw price curve
    ctx.strokeStyle = optionType === 'call' ? '#3b82f6' : '#ef4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
         for (let i = 0; i < S_values.length; i++) {
       const price = prices[i];
       if (isNaN(price) || !isFinite(price)) continue;
       
       const x = ((S_values[i] - minS) / (maxS - minS)) * width;
       const y = height - ((price - minPrice) / (maxPrice - minPrice)) * height;
       
       if (i === 0) {
         ctx.moveTo(x, y);
       } else {
         ctx.lineTo(x, y);
       }
     }
    ctx.stroke();

    // Draw axes labels
    ctx.fillStyle = '#6b7280';
    ctx.font = '12px monospace';
    
    // X-axis labels
    for (let i = 0; i <= 5; i++) {
      const x = (width * i) / 5;
      const value = minS + (maxS - minS) * (i / 5);
      const label = value >= 1000 ? `$${(value / 1000).toFixed(0)}k` : `$${value.toFixed(0)}`;
      ctx.fillText(label, x - 20, height - 5);
    }
    
    // Y-axis labels
    for (let i = 0; i <= 5; i++) {
      const y = (height * i) / 5;
      const value = maxPrice - (maxPrice - minPrice) * (i / 5);
      ctx.fillText(`$${value.toFixed(2)}`, 5, y + 10);
    }

    // Draw axis titles
    ctx.fillStyle = '#9ca3af';
    ctx.font = '14px monospace';
    ctx.fillText('Stock Price (S)', width / 2 - 50, height - 10);
    
    ctx.save();
    ctx.translate(20, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Option Price', 0, 0);
    ctx.restore();

  }, [data, optionType, K]);

  return (
    <Card className="bg-black border-gray-600 border-2 h-[400px]">
      <CardHeader className="pb-3">
        <CardTitle className="text-green-400 flex items-center gap-2 font-mono text-sm tracking-wide">
          <TrendingUp className="w-5 h-5" />
          {optionType.toUpperCase()} OPTION PRICE CURVE
        </CardTitle>
        <div className="text-gray-400 text-xs font-mono">
          K=${K.toFixed(2)}, r={(r * 100).toFixed(1)}%, σ={(sigma * 100).toFixed(1)}%, T={T.toFixed(2)}y
        </div>
      </CardHeader>
      <CardContent className="h-[320px]">
        {error && (
          <Alert className="bg-red-900/20 border-red-500 mb-4">
            <AlertCircle className="h-4 w-4 text-red-400" />
            <AlertDescription className="text-red-400 text-xs font-mono">
              {error}
            </AlertDescription>
          </Alert>
        )}
        
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-pulse bg-gray-800 h-64 w-full rounded"></div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full text-red-400">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="font-mono text-xs">CHART GENERATION FAILED</p>
            </div>
          </div>
        ) : data && data.S_values.length > 0 ? (
          <div className="relative h-full">
            <canvas
              ref={canvasRef}
              className="w-full h-full border border-gray-500 rounded"
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <TrendingUp className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="font-mono text-xs">NO DATA AVAILABLE</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
