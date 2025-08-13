"use client";

import { useState, useRef } from 'react';
import { toast, Toaster } from 'sonner';
import Controls from './components/Controls';
import PriceCard from './components/PriceCard';
import IVCard from './components/IVCard';
import GreeksTable from './components/GreeksTable';
import PriceCurve from './components/Charts/PriceCurve';
import Heatmap from './components/Charts/Heatmap';
import GreeksPanel from './components/Charts/GreeksPanel';
import { api, PriceResponse, GreeksResponse, IVResponse } from './api-client';
import { usePrice } from '@/hooks/usePrice';
import { WakeBanner } from '@/components/WakeBanner';

interface CalculationErrors {
  price?: string;
  greeks?: string;
  iv?: string;
  curve?: string;
  heatmap?: string;
  greeksCurves?: string;
}

export default function Home() {
  const { price: newPrice, waking, bannerText, lastCached, cancelAll } = usePrice();
  const abortRef = useRef<AbortController | null>(null);
  const [loading, setLoading] = useState(false);
  const [price, setPrice] = useState<number | null>(null);
  const [greeks, setGreeks] = useState<GreeksResponse | null>(null);
  const [ivData, setIvData] = useState<IVResponse | null>(null);
  const [currentParams, setCurrentParams] = useState<any>(null);
  const [errors, setErrors] = useState<CalculationErrors>({});

  const handleCalculate = async (params: any) => {
    abortRef.current?.abort();
    abortRef.current = new AbortController();
    
    setLoading(true);
    setCurrentParams(params);
    setErrors({});
    
    // Reset all data
    setPrice(null);
    setGreeks(null);
    setIvData(null);

    const newErrors: CalculationErrors = {};

    try {
      // Calculate option price using new cold-start handling
      try {
        const priceResult = await newPrice({
          S: params.S,
          K: params.K,
          r: params.r,
          q: params.q || 0,
          sigma: params.sigma,
          T: params.T,
          type: params.option_type,
        }, abortRef.current.signal);
        setPrice(priceResult.price);
      } catch (error: any) {
        const errorMsg = error.message || 'Price calculation failed';
        newErrors.price = typeof errorMsg === 'string' ? errorMsg : 'Price calculation failed';
        console.error('Price calculation error:', error);
      }

      // Calculate Greeks using existing API
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
        newErrors.greeks = typeof errorMsg === 'string' ? errorMsg : 'Greeks calculation failed';
        console.error('Greeks calculation error:', error);
      }

      // Calculate implied volatility using existing API
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
        newErrors.iv = typeof errorMsg === 'string' ? errorMsg : 'IV calculation failed';
        console.error('IV calculation error:', error);
      }

      setErrors(newErrors);

      // Show success/error messages
      const successCount = [price, greeks, ivData].filter(Boolean).length;
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
      const errorMsg = error.message || 'Unknown error';
      toast.error(`Calculation failed: ${typeof errorMsg === 'string' ? errorMsg : 'Unknown error'}`);
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
                optionType={currentParams?.option_type || 'call'}
                K={currentParams?.K || 100}
                r={currentParams?.r || 0.05}
                sigma={currentParams?.sigma || 0.2}
                T={currentParams?.T || 1.0}
                error={errors.curve}
              />
              <Heatmap 
                optionType={currentParams?.option_type || 'call'}
                K={currentParams?.K || 100}
                r={currentParams?.r || 0.05}
                T={currentParams?.T || 1.0}
                error={errors.heatmap}
              />
            </div>

            <GreeksPanel 
              optionType={currentParams?.option_type || 'call'}
              K={currentParams?.K || 100}
              r={currentParams?.r || 0.05}
              sigma={currentParams?.sigma || 0.2}
              T={currentParams?.T || 1.0}
              error={errors.greeksCurves}
            />
          </div>
        </div>
      </div>

      {waking && lastCached && (
        <div className="fixed top-4 right-4 p-3 rounded-md border bg-neutral-900 text-white text-sm max-w-md">
          <div className="text-xs opacity-70 mb-1">Showing last cached result while server wakes…</div>
          <div className="text-xs">
            <div>Price: {lastCached.price.toFixed(4)}</div>
            <div>Delta: {lastCached.greeks.delta.toFixed(4)}</div>
            <div>Gamma: {lastCached.greeks.gamma.toFixed(4)}</div>
          </div>
        </div>
      )}

      <WakeBanner 
        show={waking} 
        text={bannerText} 
        onCancel={() => {
          abortRef.current?.abort();
          cancelAll();
        }} 
      />
    </div>
  );
}
