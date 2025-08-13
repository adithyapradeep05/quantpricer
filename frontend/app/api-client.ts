import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface PriceRequest {
  S: number;
  K: number;
  r: number;
  T: number;
  sigma: number;
  option_type: "call" | "put";
}

export interface GreeksRequest {
  S: number;
  K: number;
  r: number;
  T: number;
  sigma: number;
  option_type: "call" | "put";
}

export interface IVRequest {
  market_price: number;
  S: number;
  K: number;
  r: number;
  T: number;
  option_type: "call" | "put";
}

export interface CurveRequest {
  S_values: number[];
  K: number;
  r: number;
  sigma: number;
  T: number;
  option_type: "call" | "put";
}

export interface HeatmapRequest {
  S_values: number[];
  vol_values: number[];
  K: number;
  r: number;
  T: number;
  option_type: "call" | "put";
}

export interface GreeksCurveRequest {
  S_values: number[];
  K: number;
  r: number;
  sigma: number;
  T: number;
  option_type: "call" | "put";
}

export interface PriceResponse {
  price: number;
}

export interface GreeksResponse {
  delta: number;
  gamma: number;
  vega: number;
  theta: number;
  rho: number;
}

export interface IVResponse {
  implied_vol: number;
  priced_with_iv: number;
}

export interface CurveResponse {
  S_values: number[];
  prices: number[];
}

export interface HeatmapResponse {
  z: number[][];
  S_values: number[];
  vol_values: number[];
}

export interface GreeksCurveResponse {
  S_values: number[];
  delta: number[];
  gamma: number[];
  vega: number[];
  theta: number[];
  rho: number[];
}

export const api = {
  postPrice: async (params: PriceRequest): Promise<PriceResponse> => {
    const response = await apiClient.post('/api/price', params);
    return response.data;
  },

  postGreeks: async (params: GreeksRequest): Promise<GreeksResponse> => {
    const response = await apiClient.post('/api/greeks', params);
    return response.data;
  },

  postIV: async (params: IVRequest): Promise<IVResponse> => {
    const response = await apiClient.post('/api/implied-vol', params);
    return response.data;
  },

  postCurve: async (params: CurveRequest): Promise<CurveResponse> => {
    const response = await apiClient.post('/api/curve', params);
    return response.data;
  },

  postHeatmap: async (params: HeatmapRequest): Promise<HeatmapResponse> => {
    const response = await apiClient.post('/api/heatmap', params);
    return response.data;
  },

  postGreeksCurves: async (params: GreeksCurveRequest): Promise<GreeksCurveResponse> => {
    const response = await apiClient.post('/api/greeks-curves', params);
    return response.data;
  },

  healthCheck: async (): Promise<{ status: string }> => {
    const response = await apiClient.get('/healthz');
    return response.data;
  },
};

// Helper function to generate linspace arrays
export function linspace(min: number, max: number, n: number): number[] {
  if (n <= 1) return [min];
  const step = (max - min) / (n - 1);
  return Array.from({ length: n }, (_, i) => +(min + i * step).toFixed(6));
}
