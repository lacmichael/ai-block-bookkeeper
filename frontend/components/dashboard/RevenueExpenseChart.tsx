"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartTooltip, ChartLegend } from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { mockChartData, formatCurrency } from "@/utils/mockData";

export function RevenueExpenseChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Revenue vs Expenses</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full">
          <BarChart
            data={mockChartData}
            width={500}
            height={300}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="month"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tick={{ fill: "#6b7280", fontSize: 12 }}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tick={{ fill: "#6b7280", fontSize: 12 }}
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            />
            <ChartTooltip
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="rounded-lg border bg-background p-2 shadow-md">
                      <div className="grid grid-cols-2 gap-2">
                        <div className="flex flex-col">
                          <span className="text-[0.70rem] uppercase text-muted-foreground">
                            {label}
                          </span>
                          <span className="font-bold text-muted-foreground">
                            Revenue
                          </span>
                          <span className="text-sm font-bold">
                            {formatCurrency(payload[0]?.value as number)}
                          </span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[0.70rem] uppercase text-muted-foreground">
                            {label}
                          </span>
                          <span className="font-bold text-muted-foreground">
                            Expenses
                          </span>
                          <span className="text-sm font-bold">
                            {formatCurrency(payload[1]?.value as number)}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <ChartLegend />
            <Bar
              dataKey="revenue"
              fill="#10b981"
              radius={[4, 4, 0, 0]}
              name="Revenue"
            />
            <Bar
              dataKey="expenses"
              fill="#ef4444"
              radius={[4, 4, 0, 0]}
              name="Expenses"
            />
          </BarChart>
        </div>
      </CardContent>
    </Card>
  );
}
