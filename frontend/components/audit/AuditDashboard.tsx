"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Shield,
  CheckCircle,
  XCircle,
  AlertTriangle,
  TrendingUp,
  FileText,
  RefreshCw,
  Eye,
  ArrowRight,
  Clock,
  AlertCircle,
} from "lucide-react";
import Link from "next/link";
import {
  getAuditMetrics,
  getTransactionsForAudit,
  getAuditActivity,
  getAnomalyDetection,
  AuditMetrics,
  AuditActivity,
} from "@/utils/actions/audit-actions";
import { BusinessEvent } from "@/utils/actions/business-events";
import { AuditMetadata } from "@/utils/mockAuditData";

export function AuditDashboard() {
  const [metrics, setMetrics] = useState<AuditMetrics | null>(null);
  const [pendingTransactions, setPendingTransactions] = useState<
    (BusinessEvent & { audit_metadata: AuditMetadata })[]
  >([]);
  const [recentActivity, setRecentActivity] = useState<AuditActivity[]>([]);
  const [anomalies, setAnomalies] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsData, pendingData, activityData, anomalyData] =
          await Promise.all([
            getAuditMetrics(),
            getTransactionsForAudit("pending", 5),
            getAuditActivity(10),
            getAnomalyDetection(),
          ]);

        setMetrics(metricsData);
        setPendingTransactions(pendingData);
        setRecentActivity(activityData);
        setAnomalies(anomalyData);
      } catch (error) {
        console.error("Error fetching audit data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "approved":
        return (
          <Badge variant="success" className="flex items-center gap-1">
            <CheckCircle className="h-3 w-3" />
            Approved
          </Badge>
        );
      case "rejected":
        return (
          <Badge variant="destructive" className="flex items-center gap-1">
            <XCircle className="h-3 w-3" />
            Rejected
          </Badge>
        );
      case "flagged":
        return (
          <Badge variant="warning" className="flex items-center gap-1">
            <AlertTriangle className="h-3 w-3" />
            Flagged
          </Badge>
        );
      case "pending":
        return (
          <Badge variant="secondary" className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            Pending
          </Badge>
        );
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount / 100);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span className="text-lg">Loading audit dashboard...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Pending Audits
                </p>
                <p className="text-2xl font-bold text-yellow-600">
                  {metrics?.pending_audits || 0}
                </p>
              </div>
              <Clock className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Approved
                </p>
                <p className="text-2xl font-bold text-green-600">
                  {metrics?.approved_count || 0}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Reconciliation Rate
                </p>
                <p className="text-2xl font-bold text-blue-600">
                  {metrics?.reconciliation_rate || 0}%
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Compliance Score
                </p>
                <p className="text-2xl font-bold text-purple-600">
                  {metrics?.compliance_score || 0}%
                </p>
              </div>
              <Shield className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Anomaly Alerts */}
      {anomalies?.flaggedPatterns && anomalies.flaggedPatterns.length > 0 && (
        <Card className="border-red-200 dark:border-red-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              Anomaly Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {anomalies.flaggedPatterns.map((pattern: any, index: number) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 bg-red-50 dark:bg-red-900/20 rounded"
                >
                  <span className="text-sm font-medium">{pattern.pattern}</span>
                  <Badge
                    variant={
                      pattern.severity === "high" ? "destructive" : "warning"
                    }
                  >
                    {pattern.count} occurrences
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Pending Transactions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Pending Audits
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {pendingTransactions.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  No pending audits
                </p>
              ) : (
                pendingTransactions.map((transaction) => (
                  <div
                    key={transaction.event_id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium truncate w-48">
                          {transaction.description ||
                            `Transaction ${transaction.event_id.slice(0, 8)}`}
                        </span>
                        {getStatusBadge(
                          transaction.audit_metadata.audit_status
                        )}
                      </div>
                      <div className="text-sm text-gray-500">
                        {formatCurrency(transaction.amount_minor)} •{" "}
                        {formatDate(transaction.occurred_at)}
                      </div>
                    </div>
                    <Link href={`/audit/transaction/${transaction.event_id}`}>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-1" />
                        Review
                      </Button>
                    </Link>
                  </div>
                ))
              )}
            </div>
            <div className="mt-4">
              <Link href="/transactions">
                <Button variant="outline" className="w-full">
                  View All Transactions
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 shrink-0"></div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium capitalize">
                        {activity.action}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatDate(activity.timestamp)}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {activity.details}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      by {activity.user} • Transaction{" "}
                      {activity.transaction_id.slice(0, 8)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Link href="/audit/reconciliation">
              <Button className="w-full" variant="outline">
                <ArrowRight className="h-4 w-4 mr-2" />
                Reconciliation
              </Button>
            </Link>
            <Link href="/audit/compliance">
              <Button className="w-full" variant="outline">
                <Shield className="h-4 w-4 mr-2" />
                Compliance Report
              </Button>
            </Link>
            <Button className="w-full" variant="outline">
              <FileText className="h-4 w-4 mr-2" />
              Export Report
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
