"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Activity, AlertCircle } from 'lucide-react';
import { GreeksResponse } from '../api-client';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface GreeksTableProps {
  greeks: GreeksResponse | null;
  loading: boolean;
  error?: string;
}

export default function GreeksTable({ greeks, loading, error }: GreeksTableProps) {
  const greeksData = [
    { name: 'DELTA', value: greeks?.delta, description: 'PRICE SENSITIVITY TO UNDERLYING' },
    { name: 'GAMMA', value: greeks?.gamma, description: 'DELTA SENSITIVITY TO UNDERLYING' },
    { name: 'VEGA', value: greeks?.vega, description: 'PRICE SENSITIVITY TO VOLATILITY' },
    { name: 'THETA', value: greeks?.theta, description: 'PRICE SENSITIVITY TO TIME' },
    { name: 'RHO', value: greeks?.rho, description: 'PRICE SENSITIVITY TO INTEREST RATE' },
  ];

  const formatValue = (value: number | undefined) => {
    if (value === undefined) return 'N/A';
    return value.toFixed(6);
  };

  return (
    <Card className="bg-black border-gray-600 border-2">
      <CardHeader className="pb-3">
        <CardTitle className="text-green-400 flex items-center gap-2 font-mono text-sm tracking-wide">
          <Activity className="w-5 h-5" />
          GREEKS ANALYSIS
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
        
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-gray-600">
                <TableHead className="text-gray-300 font-mono text-xs tracking-wide">GREEK</TableHead>
                <TableHead className="text-gray-300 font-mono text-xs tracking-wide">VALUE</TableHead>
                <TableHead className="text-gray-300 font-mono text-xs tracking-wide hidden md:table-cell">DESCRIPTION</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {greeksData.map((greek) => (
                <TableRow key={greek.name} className="border-gray-600">
                  <TableCell className="text-white font-mono text-sm">{greek.name}</TableCell>
                  <TableCell className="text-green-400 font-mono">
                    {loading ? (
                      <div className="animate-pulse bg-gray-800 h-4 w-16 rounded"></div>
                    ) : error ? (
                      <span className="text-red-400 text-xs">ERROR</span>
                    ) : (
                      formatValue(greek.value)
                    )}
                  </TableCell>
                  <TableCell className="text-gray-400 text-xs font-mono hidden md:table-cell">
                    {greek.description}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}