import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface TransactionChartProps {
  data: Array<{
    date: string;
    transactions: number;
    fraud: number;
  }>;
}

const TransactionChart: React.FC<TransactionChartProps> = ({ data }) => {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Évolution des Transactions
      </h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="transactions" 
              stroke="#14b8a6" 
              strokeWidth={2}
              name="Transactions"
            />
            <Line 
              type="monotone" 
              dataKey="fraud" 
              stroke="#ef4444" 
              strokeWidth={2}
              name="Fraudes"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TransactionChart;