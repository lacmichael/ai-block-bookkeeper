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
  RefreshCw,
  Download,
  FileText,
  TrendingUp,
  AlertCircle,
  Clock,
} from "lucide-react";
import {
  getComplianceReport,
  ComplianceRule,
} from "@/utils/actions/audit-actions";

export function ComplianceChecklist() {
  const [rules, setRules] = useState<ComplianceRule[]>([]);
  const [overallScore, setOverallScore] = useState(0);
  const [violations, setViolations] = useState<ComplianceRule[]>([]);
  const [warnings, setWarnings] = useState<ComplianceRule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchComplianceData();
  }, []);

  const fetchComplianceData = async () => {
    try {
      const data = await getComplianceReport();
      setRules(data.rules);
      setOverallScore(data.overallScore);
      setViolations(data.violations);
      setWarnings(data.warnings);
    } catch (error) {
      console.error("Error fetching compliance data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "high":
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case "medium":
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case "low":
        return <Clock className="h-4 w-4 text-blue-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "critical":
        return <Badge variant="destructive">Critical</Badge>;
      case "high":
        return <Badge variant="destructive">High</Badge>;
      case "medium":
        return <Badge variant="warning">Medium</Badge>;
      case "low":
        return <Badge variant="secondary">Low</Badge>;
      default:
        return <Badge variant="secondary">{severity}</Badge>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "compliant":
        return (
          <Badge variant="success" className="flex items-center gap-1">
            <CheckCircle className="h-3 w-3" />
            Compliant
          </Badge>
        );
      case "violation":
        return (
          <Badge variant="destructive" className="flex items-center gap-1">
            <XCircle className="h-3 w-3" />
            Violation
          </Badge>
        );
      case "warning":
        return (
          <Badge variant="warning" className="flex items-center gap-1">
            <AlertTriangle className="h-3 w-3" />
            Warning
          </Badge>
        );
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-600";
    if (score >= 70) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 90) return "bg-green-100 dark:bg-green-900/20";
    if (score >= 70) return "bg-yellow-100 dark:bg-yellow-900/20";
    return "bg-red-100 dark:bg-red-900/20";
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span className="text-lg">Loading compliance data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Compliance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Overall Score
                </p>
                <p
                  className={`text-3xl font-bold ${getScoreColor(
                    overallScore
                  )}`}
                >
                  {overallScore}%
                </p>
              </div>
              <div
                className={`p-3 rounded-full ${getScoreBgColor(overallScore)}`}
              >
                <Shield className={`h-8 w-8 ${getScoreColor(overallScore)}`} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Violations
                </p>
                <p className="text-3xl font-bold text-red-600">
                  {violations.length}
                </p>
              </div>
              <XCircle className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Warnings
                </p>
                <p className="text-3xl font-bold text-yellow-600">
                  {warnings.length}
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total Rules
                </p>
                <p className="text-3xl font-bold text-blue-600">
                  {rules.length}
                </p>
              </div>
              <FileText className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Critical Violations Alert */}
      {violations.length > 0 && (
        <Card className="border-red-200 dark:border-red-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              Critical Violations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {violations.map((rule) => (
                <div
                  key={rule.id}
                  className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-red-900 dark:text-red-100">
                      {rule.name}
                    </h4>
                    <div className="flex items-center gap-2">
                      {getSeverityIcon(rule.severity)}
                      {getSeverityBadge(rule.severity)}
                    </div>
                  </div>
                  <p className="text-sm text-red-700 dark:text-red-300 mb-2">
                    {rule.description}
                  </p>
                  <div className="flex items-center justify-between text-xs text-red-600">
                    <span>
                      {rule.affected_transactions} affected transactions
                    </span>
                    <span>Last checked: {formatDate(rule.last_checked)}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Compliance Rules */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Compliance Rules
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {rules.map((rule) => (
              <div key={rule.id} className="p-4 border rounded-lg">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="font-medium mb-1">{rule.name}</h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {rule.description}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    {getSeverityIcon(rule.severity)}
                    {getSeverityBadge(rule.severity)}
                    {getStatusBadge(rule.status)}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">
                      Affected Transactions:
                    </span>
                    <span className="ml-2 font-medium">
                      {rule.affected_transactions}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Last Checked:</span>
                    <span className="ml-2">
                      {formatDate(rule.last_checked)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Severity:</span>
                    <span className="ml-2 capitalize">{rule.severity}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Compliance Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <Button
              onClick={fetchComplianceData}
              disabled={loading}
              variant="outline"
              className="flex-1"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh Compliance Check
            </Button>
            <Button variant="outline" className="flex-1">
              <Download className="h-4 w-4 mr-2" />
              Export Compliance Report
            </Button>
            <Button variant="outline" className="flex-1">
              <FileText className="h-4 w-4 mr-2" />
              Generate Audit Report
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Compliance Tips */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start gap-3">
            <TrendingUp className="h-5 w-5 text-blue-500 mt-0.5" />
            <div>
              <h4 className="font-medium mb-2">Compliance Tips</h4>
              <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
                <li>
                  Review violations immediately and take corrective action
                </li>
                <li>Set up automated compliance checks for critical rules</li>
                <li>
                  Regularly update compliance rules based on regulatory changes
                </li>
                <li>Maintain documentation for all compliance decisions</li>
                <li>Schedule regular compliance training for your team</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
