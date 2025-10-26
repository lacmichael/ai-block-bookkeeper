"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartTooltip, ChartLegend } from "@/components/ui/chart";
import { PieChart, Pie, Cell } from "recharts";
import { mockTransactionTypeData, formatCurrency } from "@/lib/mockData";

const COLORS = [
  "#10b981", // Green
  "#3b82f6", // Blue
  "#f59e0b", // Amber
  "#ef4444", // Red
  "#8b5cf6", // Purple
];

const chartConfig = {};

export function TransactionsByTypeChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Transactions by Type</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full flex items-center justify-center">
          <PieChart width={300} height={300}>
            <Pie
              data={mockTransactionTypeData}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
              nameKey="type"
            >
              {mockTransactionTypeData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <ChartTooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="rounded-lg border bg-background p-2 shadow-md">
                      <div className="flex flex-col">
                        <span className="font-bold text-muted-foreground">
                          {data.type}
                        </span>
                        <span className="text-sm font-bold">
                          {formatCurrency(data.value)}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {data.count} transactions
                        </span>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <ChartLegend />
          </PieChart>
        </div>
      </CardContent>
    </Card>
  );
}
