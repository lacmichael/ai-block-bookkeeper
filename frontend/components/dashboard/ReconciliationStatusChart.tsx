"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartTooltip, ChartLegend } from "@/components/ui/chart";
import { PieChart, Pie, Cell } from "recharts";
import { mockReconciliationData, formatCurrency } from "@/utils/mockData";

const COLORS = [
  "#10b981", // Reconciled - Green
  "#ef4444", // Unreconciled - Red
  "#f59e0b", // Partial - Yellow
];

export function ReconciliationStatusChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Reconciliation Status</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full flex items-center justify-center">
          <PieChart width={300} height={300}>
            <Pie
              data={mockReconciliationData as any}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={5}
              dataKey="value"
              nameKey="status"
            >
              {mockReconciliationData.map((_entry, index) => (
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
                          {data.status}
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
