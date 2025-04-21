"use client";

import React from 'react';

interface FinancialData {
  date: string;
  total_income: number;
  total_expense: number;
  total_debt: number;
  balance: number;
}

interface FinancialChartProps {
  data: FinancialData[];
}

export function FinancialChart({ data }: FinancialChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full w-full flex items-center justify-center">
        <p className="text-muted-foreground">Không có dữ liệu để hiển thị</p>
      </div>
    );
  }

  const maxValue = Math.max(
    ...data.flatMap(item => [
      item.total_income,
      item.total_expense,
      item.total_debt,
      item.balance
    ])
  );

  // Determine height of bars based on value
  const getHeight = (value: number) => {
    return `${(value / maxValue) * 100}%`;
  };

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex-1 relative flex items-end">
        {data.map((item, index) => (
          <div key={index} className="group flex-1 flex justify-center gap-1 h-full pb-6 pt-6">
            <div className="relative h-full w-full max-w-[30px] flex flex-col items-center justify-end">
              {/* Income bar */}
              <div
                style={{ height: getHeight(item.total_income) }}
                className="w-full bg-primary rounded-t-sm"
              />
              {/* Tooltip */}
              <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-black text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                Thu nhập: {item.total_income.toLocaleString()}đ
              </div>
            </div>
            
            <div className="relative h-full w-full max-w-[30px] flex flex-col items-center justify-end">
              {/* Expense bar */}
              <div
                style={{ height: getHeight(item.total_expense) }}
                className="w-full bg-destructive rounded-t-sm"
              />
              {/* Tooltip */}
              <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-black text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                Chi tiêu: {item.total_expense.toLocaleString()}đ
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* X Axis - Dates */}
      <div className="grid grid-flow-col auto-cols-fr text-xs text-muted-foreground">
        {data.map((item, index) => (
          <div key={index} className="text-center truncate px-1">
            {new Date(item.date).toLocaleDateString('vi-VN')}
          </div>
        ))}
      </div>
      
      {/* Legend */}
      <div className="flex justify-center gap-4 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-primary rounded-sm"></div>
          <span className="text-xs">Thu nhập</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-destructive rounded-sm"></div>
          <span className="text-xs">Chi tiêu</span>
        </div>
      </div>
    </div>
  );
} 