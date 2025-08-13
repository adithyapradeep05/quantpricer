"use client";

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { api, linspace } from '../../api-client';

interface GreeksPanelProps {
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

interface GreeksData {
  S_values: number[];
  delta: number[];
  gamma: number[];
  vega: number[];
  theta: number[];
  rho: number[];
}

export default function GreeksPanel({ 
  optionType, 
  K, 
  r, 
  sigma, 
  T, 
  Smin, 
  Smax, 
  points = 201,
  error: propError 
}: GreeksPanelProps) {
  const [data, setData] = useState<GreeksData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(propError || null);
  const canvasRefs = useRef<(HTMLCanvasElement | null)[]>([]);

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
        
        const response = await api.postGreeksCurves({
          S_values,
          K,
          r,
          sigma,
          T,
          option_type: optionType,
        });

        setData({
          S_values: response.S_values,
          delta: response.delta,
          gamma: response.gamma,
          vega: response.vega,
          theta: response.theta,
          rho: response.rho
        });
             } catch (err: any) {
         console.error('Error fetching Greeks curves data:', err);
         const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch Greeks curves data';
         setError(typeof errorMessage === 'string' ? errorMessage : 'Failed to fetch Greeks curves data');
       } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [optionType, K, r, sigma, T, defaultSmin, defaultSmax, points]);

  useEffect(() => {
    if (!data) return;

    const greeksConfig = [
      { name: 'Delta', data: data.delta, color: '#3b82f6' },
      { name: 'Gamma', data: data.gamma, color: '#10b981' },
      { name: 'Vega', data: data.vega, color: '#8b5cf6' },
      { name: 'Theta', data: data.theta, color: '#f59e0b' },
      { name: 'Rho', data: data.rho, color: '#ec4899' }
    ];

    greeksConfig.forEach((config, index) => {
      const canvas = canvasRefs.current[index];
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const width = canvas.offsetWidth;
      const height = canvas.offsetHeight;
      canvas.width = width;
      canvas.height = height;

      // Clear canvas
      ctx.clearRect(0, 0, width, height);

      if (data.S_values.length === 0) return;

             // Find min and max values for scaling
       const validGreekData = config.data.filter(val => !isNaN(val) && isFinite(val));
       if (validGreekData.length === 0) return;
       
       const minS = Math.min(...data.S_values);
       const maxS = Math.max(...data.S_values);
       const minGreek = Math.min(...validGreekData);
       const maxGreek = Math.max(...validGreekData);

      // Draw grid
      ctx.strokeStyle = '#374151';
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      
      // Vertical grid lines
      for (let i = 0; i <= 3; i++) {
        const x = (width * i) / 3;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      
      // Horizontal grid lines
      for (let i = 0; i <= 3; i++) {
        const y = (height * i) / 3;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }
      ctx.setLineDash([]);

      // Draw strike line
      const strikeX = ((K - minS) / (maxS - minS)) * width;
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(strikeX, 0);
      ctx.lineTo(strikeX, height);
      ctx.stroke();
      ctx.setLineDash([]);

      // Draw Greek curve
      ctx.strokeStyle = config.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      
             for (let i = 0; i < data.S_values.length; i++) {
         const greekValue = config.data[i];
         if (isNaN(greekValue) || !isFinite(greekValue)) continue;
         
         const x = ((data.S_values[i] - minS) / (maxS - minS)) * width;
         const y = height - ((greekValue - minGreek) / (maxGreek - minGreek)) * height;
         
         if (i === 0) {
           ctx.moveTo(x, y);
         } else {
           ctx.lineTo(x, y);
         }
       }
      ctx.stroke();

      // Draw title
      ctx.fillStyle = '#9ca3af';
      ctx.font = '10px monospace';
      ctx.fillText(config.name, 5, 15);
    });

  }, [data, K]);

  return (
    <Card className="bg-black border-gray-600 border-2">
      <CardHeader className="pb-3">
        <CardTitle className="text-green-400 flex items-center gap-2 font-mono text-sm tracking-wide">
          <Activity className="w-5 h-5" />
          GREEKS CURVES - {optionType.toUpperCase()} OPTION
        </CardTitle>
        <div className="text-gray-400 text-xs font-mono">
          K=${K.toFixed(2)}, r={(r * 100).toFixed(1)}%, σ={(sigma * 100).toFixed(1)}%, T={T.toFixed(2)}y
        </div>
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
        
        {loading ? (
          <div className="grid grid-cols-5 gap-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="animate-pulse bg-gray-800 h-32 rounded"></div>
            ))}
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-32 text-red-400">
            <div className="text-center">
              <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="font-mono text-xs">GREEKS CURVES FAILED</p>
            </div>
          </div>
        ) : data ? (
          <div className="grid grid-cols-5 gap-4">
            {['Delta', 'Gamma', 'Vega', 'Theta', 'Rho'].map((greek, index) => (
              <div key={greek} className="h-32">
                <canvas
                  ref={(el) => canvasRefs.current[index] = el}
                  className="w-full h-full border border-gray-500 rounded"
                />
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center h-32 text-gray-500">
            <div className="text-center">
              <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="font-mono text-xs">NO DATA AVAILABLE</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
