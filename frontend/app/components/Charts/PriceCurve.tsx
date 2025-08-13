"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useEffect, useRef } from 'react';
import { TrendingUp, AlertCircle } from 'lucide-react';
import { CurveResponse } from '../../api-client';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface PriceCurveProps {
  data: CurveResponse | null;
  loading: boolean;
  optionType: 'call' | 'put';
  error?: string;
}

export default function PriceCurve({ data, loading, optionType, error }: PriceCurveProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

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
    const minS = Math.min(...S_values);
    const maxS = Math.max(...S_values);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);

    // Draw grid
    ctx.strokeStyle = '#333333';
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

    // Draw price curve
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    for (let i = 0; i < S_values.length; i++) {
      const x = ((S_values[i] - minS) / (maxS - minS)) * width;
      const y = height - ((prices[i] - minPrice) / (maxPrice - minPrice)) * height;
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();

    // Draw data points
    ctx.fillStyle = '#00ff00';
    for (let i = 0; i < S_values.length; i += Math.ceil(S_values.length / 20)) {
      const x = ((S_values[i] - minS) / (maxS - minS)) * width;
      const y = height - ((prices[i] - minPrice) / (maxPrice - minPrice)) * height;
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, 2 * Math.PI);
      ctx.fill();
    }

    // Draw axes labels
    ctx.fillStyle = '#666666';
    ctx.font = '10px monospace';
    
    // X-axis labels
    for (let i = 0; i <= 5; i++) {
      const x = (width * i) / 5;
      const value = minS + (maxS - minS) * (i / 5);
      ctx.fillText(`$${value.toFixed(0)}`, x, height - 5);
    }
    
    // Y-axis labels
    for (let i = 0; i <= 5; i++) {
      const y = (height * i) / 5;
      const value = maxPrice - (maxPrice - minPrice) * (i / 5);
      ctx.fillText(`$${value.toFixed(2)}`, 5, y + 10);
    }

  }, [data]);

  return (
    <Card className="bg-black border-gray-600 border-2 h-[400px]">
      <CardHeader className="pb-3">
        <CardTitle className="text-green-400 flex items-center gap-2 font-mono text-sm tracking-wide">
          <TrendingUp className="w-5 h-5" />
          PRICE CURVE - {optionType.toUpperCase()} OPTION
        </CardTitle>
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
