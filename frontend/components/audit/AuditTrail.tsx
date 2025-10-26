"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Upload,
  FileText,
  Zap,
  Shield,
  CheckCircle,
  Clock,
  AlertCircle,
  ArrowRight,
} from "lucide-react";
import { BusinessEvent } from "@/utils/actions/business-events";
import { AuditMetadata } from "@/utils/mockAuditData";

interface AuditTrailProps {
  transaction: BusinessEvent & { audit_metadata: AuditMetadata };
}

export function AuditTrail({ transaction }: AuditTrailProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case "failed":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "success":
        return <Badge variant="success">Completed</Badge>;
      case "pending":
        return <Badge variant="warning">Pending</Badge>;
      case "failed":
        return <Badge variant="destructive">Failed</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  // Mock audit trail steps
  const auditSteps = [
    {
      id: "upload",
      title: "Document Upload",
      description: "Invoice document uploaded to system",
      timestamp: new Date(transaction.occurred_at).toISOString(),
      status: "success",
      icon: Upload,
      details: {
        filename: "invoice_001.pdf",
        size: "2.3 MB",
        hash: "sha256:abc123...",
      },
    },
    {
      id: "extraction",
      title: "Data Extraction",
      description: "AI extracted transaction data from document",
      timestamp: new Date(
        new Date(transaction.occurred_at).getTime() + 30000
      ).toISOString(),
      status: "success",
      icon: FileText,
      details: {
        confidence: "95%",
        fields_extracted: ["amount", "date", "vendor", "description"],
        processing_time: "2.3s",
      },
    },
    {
      id: "validation",
      title: "Data Validation",
      description: "Business rules and validation checks applied",
      timestamp: new Date(
        new Date(transaction.occurred_at).getTime() + 60000
      ).toISOString(),
      status: "success",
      icon: Zap,
      details: {
        rules_passed: 8,
        rules_failed: 0,
        risk_score: transaction.audit_metadata.risk_score || 25,
      },
    },
    {
      id: "blockchain",
      title: "Blockchain Recording",
      description: "Transaction recorded on Sui blockchain",
      timestamp: new Date(
        new Date(transaction.occurred_at).getTime() + 90000
      ).toISOString(),
      status:
        transaction.audit_metadata.verification_status === "verified"
          ? "success"
          : "pending",
      icon: Shield,
      details: {
        digest: "0x1234...5678",
        block_height: 50012345,
        confirmations: 12,
        gas_used: "1,234 SUI",
      },
    },
    {
      id: "audit",
      title: "Audit Review",
      description: "Human audit review and decision",
      timestamp: transaction.audit_metadata.audited_at || null,
      status:
        transaction.audit_metadata.audit_status === "pending"
          ? "pending"
          : "success",
      icon: CheckCircle,
      details: {
        auditor: transaction.audit_metadata.audited_by || "Pending",
        decision: transaction.audit_metadata.audit_status,
        notes: transaction.audit_metadata.audit_notes || "No notes",
      },
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ArrowRight className="h-5 w-5" />
          Audit Trail
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {auditSteps.map((step, index) => {
            const Icon = step.icon;
            const isLast = index === auditSteps.length - 1;

            return (
              <div key={step.id} className="relative">
                <div className="flex items-start gap-3">
                  <div className="shrink-0">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        step.status === "success"
                          ? "bg-green-100 dark:bg-green-900"
                          : step.status === "failed"
                          ? "bg-red-100 dark:bg-red-900"
                          : "bg-yellow-100 dark:bg-yellow-900"
                      }`}
                    >
                      <Icon
                        className={`h-4 w-4 ${
                          step.status === "success"
                            ? "text-green-600"
                            : step.status === "failed"
                            ? "text-red-600"
                            : "text-yellow-600"
                        }`}
                      />
                    </div>
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium">{step.title}</h4>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(step.status)}
                        {getStatusBadge(step.status)}
                      </div>
                    </div>

                    <p className="text-sm text-gray-600 mt-1">
                      {step.description}
                    </p>

                    {step.timestamp && (
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDate(step.timestamp)}
                      </p>
                    )}

                    {/* Step Details */}
                    {step.details && (
                      <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs">
                        {Object.entries(step.details).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-gray-600 capitalize">
                              {key.replace(/_/g, " ")}:
                            </span>
                            <span className="font-medium">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Connecting Line */}
                {!isLast && (
                  <div className="absolute left-4 top-8 w-px h-6 bg-gray-200 dark:bg-gray-700"></div>
                )}
              </div>
            );
          })}
        </div>

        {/* Summary */}
        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
            Audit Summary
          </h4>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-blue-700 dark:text-blue-300">
                Transaction ID:
              </span>
              <span className="ml-2 font-mono">{transaction.event_id}</span>
            </div>
            <div>
              <span className="text-blue-700 dark:text-blue-300">
                Source System:
              </span>
              <span className="ml-2">{transaction.source_system}</span>
            </div>
            <div>
              <span className="text-blue-700 dark:text-blue-300">Amount:</span>
              <span className="ml-2 font-medium">
                {new Intl.NumberFormat("en-US", {
                  style: "currency",
                  currency: "USD",
                }).format(transaction.amount_minor / 100)}
              </span>
            </div>
            <div>
              <span className="text-blue-700 dark:text-blue-300">Status:</span>
              <span className="ml-2 capitalize">
                {transaction.audit_metadata.audit_status}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
