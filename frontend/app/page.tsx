"use client";

import { useState } from 'react';
import { toast, Toaster } from 'sonner';
import Controls from './components/Controls';
import PriceCard from './components/PriceCard';
import IVCard from './components/IVCard';
import GreeksTable from './components/GreeksTable';
import PriceCurve from './components/Charts/PriceCurve';
import Heatmap from './components/Charts/Heatmap';
import { api, PriceResponse, GreeksResponse, IVResponse, CurveResponse, HeatmapResponse } from './api-client';

interface CalculationErrors {
  price?: string;
  greeks?: string;
  iv?: string;
  curve?: string;
  heatmap?: string;
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [price, setPrice] = useState<number | null>(null);
  const [greeks, setGreeks] = useState<GreeksResponse | null>(null);
  const [ivData, setIvData] = useState<IVResponse | null>(null);
  const [curveData, setCurveData] = useState<CurveResponse | null>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapResponse | null>(null);
  const [currentParams, setCurrentParams] = useState<any>(null);
  const [errors, setErrors] = useState<CalculationErrors>({});

  const handleCalculate = async (params: any) => {
    setLoading(true);
    setCurrentParams(params);
    setErrors({});
    
    // Reset all data
    setPrice(null);
    setGreeks(null);
    setIvData(null);
    setCurveData(null);
    setHeatmapData(null);

    const newErrors: CalculationErrors = {};

    try {
      // Calculate option price
      try {
        const priceResult = await api.postPrice({
          S: params.S,
          K: params.K,
          r: params.r,
          T: params.T,
          sigma: params.sigma,
          option_type: params.option_type,
        });
        setPrice(priceResult.price);
      } catch (error: any) {
        const errorMsg = error.response?.data?.detail || error.message || 'Price calculation failed';
        newErrors.price = errorMsg;
        console.error('Price calculation error:', error);
      }

      // Calculate Greeks
      try {
        const greeksResult = await api.postGreeks({
          S: params.S,
          K: params.K,
          r: params.r,
          T: params.T,
          sigma: params.sigma,
          option_type: params.option_type,
        });
        setGreeks(greeksResult);
      } catch (error: any) {
        const errorMsg = error.response?.data?.detail || error.message || 'Greeks calculation failed';
        newErrors.greeks = errorMsg;
        console.error('Greeks calculation error:', error);
      }

      // Calculate implied volatility
      try {
        const ivResult = await api.postIV({
          market_price: params.market_price,
          S: params.S,
          K: params.K,
          r: params.r,
          T: params.T,
          option_type: params.option_type,
        });
        setIvData(ivResult);
      } catch (error: any) {
        const errorMsg = error.response?.data?.detail || error.message || 'IV calculation failed';
        newErrors.iv = errorMsg;
        console.error('IV calculation error:', error);
      }

      // Generate price curve
      try {
        const S_range = Array.from({ length: 50 }, (_, i) => params.S * (0.5 + i * 0.03));
        const curveResult = await api.postCurve({
          S_values: S_range,
          K: params.K,
          r: params.r,
          sigma: params.sigma,
          T: params.T,
          option_type: params.option_type,
        });
        setCurveData(curveResult);
      } catch (error: any) {
        const errorMsg = error.response?.data?.detail || error.message || 'Curve generation failed';
        newErrors.curve = errorMsg;
        console.error('Curve generation error:', error);
      }

      // Generate heatmap
      try {
        const vol_range = Array.from({ length: 20 }, (_, i) => 0.1 + i * 0.02);
        const S_heatmap = Array.from({ length: 20 }, (_, i) => params.S * (0.7 + i * 0.03));
        const heatmapResult = await api.postHeatmap({
          S_values: S_heatmap,
          vol_values: vol_range,
          K: params.K,
          r: params.r,
          T: params.T,
          option_type: params.option_type,
        });
        setHeatmapData(heatmapResult);
      } catch (error: any) {
        const errorMsg = error.response?.data?.detail || error.message || 'Heatmap generation failed';
        newErrors.heatmap = errorMsg;
        console.error('Heatmap generation error:', error);
      }

      setErrors(newErrors);

      // Show success/error messages
      const successCount = [price, greeks, ivData, curveData, heatmapData].filter(Boolean).length;
      const errorCount = Object.keys(newErrors).length;
      
      if (errorCount === 0) {
        toast.success('All calculations completed successfully');
      } else if (successCount > 0) {
        toast.success(`${successCount} calculations completed, ${errorCount} failed`);
      } else {
        toast.error('All calculations failed. Please check your inputs.');
      }

    } catch (error: any) {
      console.error('General calculation error:', error);
      toast.error(`Calculation failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <Toaster theme="dark" />
      
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 text-green-400 font-mono tracking-wider">
            QuantPricer
          </h1>
          <p className="text-gray-300 text-lg font-mono">PROFESSIONAL OPTION PRICING TERMINAL</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <Controls onCalculate={handleCalculate} loading={loading} />
          </div>

          <div className="lg:col-span-3 space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <PriceCard 
                price={price} 
                optionType={currentParams?.option_type || 'call'} 
                loading={loading}
                error={errors.price}
              />
              <IVCard 
                impliedVol={ivData?.implied_vol || null}
                pricedWithIV={ivData?.priced_with_iv || null}
                loading={loading}
                error={errors.iv}
              />
            </div>

            <GreeksTable greeks={greeks} loading={loading} error={errors.greeks} />

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
              <PriceCurve 
                data={curveData} 
                loading={loading}
                optionType={currentParams?.option_type || 'call'}
                error={errors.curve}
              />
              <Heatmap 
                data={heatmapData} 
                loading={loading}
                optionType={currentParams?.option_type || 'call'}
                error={errors.heatmap}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
