"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Receipt,
  Calculator,
  CheckCircle,
} from "lucide-react";
import {
  mockFinancialMetrics,
  formatCurrency,
  formatPercentage,
} from "@/lib/mockData";

export function MetricsCards() {
  const metrics = mockFinancialMetrics;

  const getTrendIcon = (change: number) => {
    return change >= 0 ? (
      <TrendingUp className="h-4 w-4 text-green-600" />
    ) : (
      <TrendingDown className="h-4 w-4 text-red-600" />
    );
  };

  const getTrendColor = (change: number) => {
    return change >= 0 ? "text-green-600" : "text-red-600";
  };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {/* Total Revenue */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatCurrency(metrics.totalRevenue)}
          </div>
          <div className="flex items-center space-x-1 text-xs text-muted-foreground">
            {getTrendIcon(metrics.revenueChange)}
            <span className={getTrendColor(metrics.revenueChange)}>
              {formatPercentage(metrics.revenueChange)}
            </span>
            <span>from last month</span>
          </div>
        </CardContent>
      </Card>

      {/* Total Expenses */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Expenses</CardTitle>
          <Receipt className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatCurrency(metrics.totalExpenses)}
          </div>
          <div className="flex items-center space-x-1 text-xs text-muted-foreground">
            {getTrendIcon(metrics.expenseChange)}
            <span className={getTrendColor(metrics.expenseChange)}>
              {formatPercentage(metrics.expenseChange)}
            </span>
            <span>from last month</span>
          </div>
        </CardContent>
      </Card>

      {/* Net Profit */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Net Profit</CardTitle>
          <Calculator className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatCurrency(metrics.netProfit)}
          </div>
          <div className="flex items-center space-x-1 text-xs text-muted-foreground">
            {getTrendIcon(metrics.profitChange)}
            <span className={getTrendColor(metrics.profitChange)}>
              {formatPercentage(metrics.profitChange)}
            </span>
            <span>from last month</span>
          </div>
        </CardContent>
      </Card>

      {/* Reconciliation Rate */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Reconciliation Rate
          </CardTitle>
          <CheckCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {metrics.reconciliationRate}%
          </div>
          <div className="flex items-center space-x-1 text-xs text-muted-foreground">
            {getTrendIcon(metrics.reconciliationChange)}
            <span className={getTrendColor(metrics.reconciliationChange)}>
              {formatPercentage(metrics.reconciliationChange)}
            </span>
            <span>from last month</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
