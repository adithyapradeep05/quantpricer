"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useEffect, useRef } from 'react';
import { Zap } from 'lucide-react';
import { HeatmapResponse } from '../../api-client';

interface HeatmapProps {
  data: HeatmapResponse | null;
  loading: boolean;
  optionType: 'call' | 'put';
}

export default function Heatmap({ data, loading, optionType }: HeatmapProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

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
    const flatZ = z.flat();
    const minZ = Math.min(...flatZ);
    const maxZ = Math.max(...flatZ);

    // Draw heatmap
    for (let i = 0; i < rows; i++) {
      for (let j = 0; j < cols; j++) {
        const value = z[i][j];
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

  }, [data]);

  return (
    <Card className="bg-black border-gray-600 border-2 h-[400px]">
      <CardHeader className="pb-3">
        <CardTitle className="text-green-400 flex items-center gap-2 font-mono text-sm tracking-wide">
          <Zap className="w-5 h-5" />
          VOLATILITY HEATMAP - {optionType.toUpperCase()} OPTION
        </CardTitle>
      </CardHeader>
      <CardContent className="h-[320px]">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-pulse bg-gray-800 h-64 w-full rounded"></div>
          </div>
        ) : data ? (
          <div className="relative h-full">
            <canvas
              ref={canvasRef}
              className="w-full h-full border border-gray-500 rounded"
              style={{ imageRendering: 'pixelated' }}
            />
            <div className="absolute bottom-2 right-2 bg-black bg-opacity-90 rounded p-2 border border-gray-600">
              <div className="flex items-center gap-2 text-xs text-gray-300 font-mono">
                <div className="w-3 h-3 bg-blue-500 rounded"></div>
                <span>LOW</span>
                <div className="w-8 h-3 bg-gradient-to-r from-blue-500 to-red-500 rounded"></div>
                <div className="w-3 h-3 bg-red-500 rounded"></div>
                <span>HIGH</span>
              </div>
            </div>
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
