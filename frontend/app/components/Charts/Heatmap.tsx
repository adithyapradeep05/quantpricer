"use client";

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Zap, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { api, linspace } from '../../api-client';

interface HeatmapProps {
  optionType: 'call' | 'put';
  K: number;
  r: number;
  T: number;
  Smin?: number;
  Smax?: number;
  Spoints?: number;
  sigmaMin?: number;
  sigmaMax?: number;
  sigmaPoints?: number;
  error?: string;
}

export default function Heatmap({ 
  optionType, 
  K, 
  r, 
  T, 
  Smin, 
  Smax, 
  Spoints = 151,
  sigmaMin = 0.05,
  sigmaMax = 0.5,
  sigmaPoints = 51,
  error: propError 
}: HeatmapProps) {
  const [data, setData] = useState<{ z: number[][], S_values: number[], vol_values: number[] } | null>(null);
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
      if (!K || !r || !T) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const S_values = linspace(defaultSmin, defaultSmax, Spoints);
        const vol_values = linspace(sigmaMin, sigmaMax, sigmaPoints);
        
        const response = await api.postHeatmap({
          S_values,
          vol_values,
          K,
          r,
          T,
          option_type: optionType,
        });

        setData({
          z: response.z,
          S_values: response.S_values,
          vol_values: response.vol_values
        });
             } catch (err: any) {
         console.error('Error fetching heatmap data:', err);
         const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch heatmap data';
         setError(typeof errorMessage === 'string' ? errorMessage : 'Failed to fetch heatmap data');
       } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [optionType, K, r, T, defaultSmin, defaultSmax, Spoints, sigmaMin, sigmaMax, sigmaPoints]);

  useEffect(() => {
    if (!data || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { z, S_values, vol_values } = data;
    
    // Set canvas size
    const width = canvas.offsetWidth;
    const height = canvas.offsetHeight;
    canvas.width = width;
    canvas.height = height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    if (z.length === 0 || z[0].length === 0) return;

    const rows = z.length;
    const cols = z[0].length;
    const cellWidth = width / cols;
    const cellHeight = height / rows;

         // Find min and max values for color scaling
     const flatZ = z.flat().filter(val => !isNaN(val) && isFinite(val));
     if (flatZ.length === 0) return;
     
     const minZ = Math.min(...flatZ);
     const maxZ = Math.max(...flatZ);

    // Draw heatmap
           for (let i = 0; i < rows; i++) {
         for (let j = 0; j < cols; j++) {
           const value = z[i][j];
           if (isNaN(value) || !isFinite(value)) {
             ctx.fillStyle = '#374151'; // Gray for invalid values
             ctx.fillRect(j * cellWidth, i * cellHeight, cellWidth, cellHeight);
             continue;
           }
           
           const normalized = (value - minZ) / (maxZ - minZ);
           
           // Create color based on normalized value (blue to red gradient)
           const red = Math.floor(normalized * 255);
           const blue = Math.floor((1 - normalized) * 255);
           const green = Math.floor(normalized * 128);
           
           ctx.fillStyle = `rgb(${red}, ${green}, ${blue})`;
           ctx.fillRect(j * cellWidth, i * cellHeight, cellWidth, cellHeight);
         }
       }

    // Add grid lines
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 0.5;
    
    // Vertical lines
    for (let j = 0; j <= cols; j++) {
      const x = j * cellWidth;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    
    // Horizontal lines
    for (let i = 0; i <= rows; i++) {
      const y = i * cellHeight;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

         // Draw strike line
     const strikeIndex = S_values.findIndex(S => S >= K);
     if (strikeIndex !== -1 && strikeIndex < cols) {
       const strikeX = (strikeIndex / cols) * width;
       ctx.strokeStyle = '#ef4444';
       ctx.lineWidth = 2;
       ctx.setLineDash([6, 6]);
       ctx.beginPath();
       ctx.moveTo(strikeX, 0);
       ctx.lineTo(strikeX, height);
       ctx.stroke();
       ctx.setLineDash([]);
     }

    // Draw axes labels
    ctx.fillStyle = '#6b7280';
    ctx.font = '10px monospace';
    
         // X-axis labels (stock prices)
     for (let i = 0; i <= 4; i++) {
       const x = (width * i) / 4;
       const index = Math.floor((i / 4) * (S_values.length - 1));
       if (index >= 0 && index < S_values.length) {
         const value = S_values[index];
         const label = value >= 1000 ? `$${(value / 1000).toFixed(0)}k` : `$${value.toFixed(0)}`;
         ctx.fillText(label, x - 15, height - 5);
       }
     }
     
     // Y-axis labels (volatilities)
     for (let i = 0; i <= 4; i++) {
       const y = (height * i) / 4;
       const index = Math.floor((i / 4) * (vol_values.length - 1));
       if (index >= 0 && index < vol_values.length) {
         const value = vol_values[index];
         ctx.fillText(`${(value * 100).toFixed(0)}%`, 5, y + 10);
       }
     }

    // Draw axis titles
    ctx.fillStyle = '#9ca3af';
    ctx.font = '12px monospace';
    ctx.fillText('Stock Price (S)', width / 2 - 40, height - 10);
    
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Volatility (σ)', 0, 0);
    ctx.restore();

    // Draw color legend
    const legendWidth = 200;
    const legendHeight = 20;
    const legendX = width - legendWidth - 10;
    const legendY = 10;
    
    // Legend gradient
    const gradient = ctx.createLinearGradient(legendX, legendY, legendX + legendWidth, legendY);
    gradient.addColorStop(0, 'rgb(0, 0, 255)'); // Blue
    gradient.addColorStop(0.5, 'rgb(128, 128, 0)'); // Green
    gradient.addColorStop(1, 'rgb(255, 0, 0)'); // Red
    
    ctx.fillStyle = gradient;
    ctx.fillRect(legendX, legendY, legendWidth, legendHeight);
    
    // Legend border
    ctx.strokeStyle = '#6b7280';
    ctx.lineWidth = 1;
    ctx.strokeRect(legendX, legendY, legendWidth, legendHeight);
    
    // Legend labels
    ctx.fillStyle = '#9ca3af';
    ctx.font = '10px monospace';
    ctx.fillText('LOW', legendX - 25, legendY + 15);
    ctx.fillText('HIGH', legendX + legendWidth + 5, legendY + 15);

  }, [data, K]);

  return (
    <Card className="bg-black border-gray-600 border-2 h-[400px]">
      <CardHeader className="pb-3">
        <CardTitle className="text-green-400 flex items-center gap-2 font-mono text-sm tracking-wide">
          <Zap className="w-5 h-5" />
          {optionType.toUpperCase()} OPTION PRICE HEATMAP
        </CardTitle>
        <div className="text-gray-400 text-xs font-mono">
          K=${K.toFixed(2)}, r={(r * 100).toFixed(1)}%, T={T.toFixed(2)}y
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
              <p className="font-mono text-xs">HEATMAP GENERATION FAILED</p>
            </div>
          </div>
        ) : data ? (
          <div className="relative h-full">
            <canvas
              ref={canvasRef}
              className="w-full h-full border border-gray-500 rounded"
              style={{ imageRendering: 'pixelated' }}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <Zap className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="font-mono text-xs">NO DATA AVAILABLE</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
