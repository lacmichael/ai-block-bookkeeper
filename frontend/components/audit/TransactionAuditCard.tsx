"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Shield,
  FileText,
  DollarSign,
  Calendar,
  User,
  Building,
  MessageSquare,
} from "lucide-react";
import { BusinessEvent } from "@/utils/actions/business-events";
import { AuditMetadata } from "@/utils/mockAuditData";
import { submitAuditDecision } from "@/utils/actions/audit-actions";

interface TransactionAuditCardProps {
  transaction: BusinessEvent & { audit_metadata: AuditMetadata };
}

export function TransactionAuditCard({
  transaction,
}: TransactionAuditCardProps) {
  const [decision, setDecision] = useState<string | null>(null);
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  // Safety check for audit_metadata
  if (!transaction.audit_metadata) {
    return (
      <div className="p-4 text-center text-gray-500">
        Loading audit information...
      </div>
    );
  }

  const handleDecision = async (
    decisionType: "approve" | "reject" | "flag"
  ) => {
    setIsSubmitting(true);
    try {
      await submitAuditDecision(transaction.event_id, decisionType, notes);
      setDecision(decisionType);
      setSubmitted(true);
    } catch (error) {
      console.error("Error submitting decision:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

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

  const getComplianceBadge = (status: string) => {
    switch (status) {
      case "compliant":
        return (
          <Badge variant="success" className="flex items-center gap-1">
            <CheckCircle className="h-3 w-3" />
            Compliant
          </Badge>
        );
      case "non_compliant":
        return (
          <Badge variant="destructive" className="flex items-center gap-1">
            <XCircle className="h-3 w-3" />
            Non-Compliant
          </Badge>
        );
      case "requires_review":
        return (
          <Badge variant="warning" className="flex items-center gap-1">
            <AlertTriangle className="h-3 w-3" />
            Review Required
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
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getRiskColor = (score: number) => {
    if (score >= 70) return "text-red-600";
    if (score >= 40) return "text-yellow-600";
    return "text-green-600";
  };

  return (
    <div className="space-y-6">
      {/* Transaction Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Transaction Audit
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Status and Compliance */}
          <div className="flex items-center gap-4">
            {getStatusBadge(transaction.audit_metadata.audit_status)}
            {getComplianceBadge(
              transaction.audit_metadata.compliance_status || "compliant"
            )}
            {transaction.audit_metadata.risk_score && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Risk Score:</span>
                <span
                  className={`font-medium ${getRiskColor(
                    transaction.audit_metadata.risk_score
                  )}`}
                >
                  {transaction.audit_metadata.risk_score}/100
                </span>
              </div>
            )}
          </div>

          {/* Transaction Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-gray-400" />
                <span className="text-sm font-medium">Amount:</span>
                <span className="text-lg font-bold">
                  {formatCurrency(transaction.amount_minor)}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-gray-400" />
                <span className="text-sm font-medium">Date:</span>
                <span className="text-sm">
                  {formatDate(transaction.occurred_at)}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-gray-400" />
                <span className="text-sm font-medium">Type:</span>
                <Badge variant="outline">{transaction.event_kind}</Badge>
              </div>
            </div>
            <div className="space-y-3">
              {transaction.payer_party && (
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-gray-400" />
                  <span className="text-sm font-medium">Payer:</span>
                  <span className="text-sm">
                    {transaction.payer_party.display_name}
                  </span>
                </div>
              )}
              {transaction.payee_party && (
                <div className="flex items-center gap-2">
                  <Building className="h-4 w-4 text-gray-400" />
                  <span className="text-sm font-medium">Payee:</span>
                  <span className="text-sm">
                    {transaction.payee_party.display_name}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Description */}
          {transaction.description && (
            <div>
              <span className="text-sm font-medium">Description:</span>
              <p className="text-sm text-gray-600 mt-1">
                {transaction.description}
              </p>
            </div>
          )}

          {/* Anomaly Flags */}
          {transaction.audit_metadata.anomaly_flags &&
            transaction.audit_metadata.anomaly_flags.length > 0 && (
              <div>
                <span className="text-sm font-medium text-red-600">
                  Anomaly Flags:
                </span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {transaction.audit_metadata.anomaly_flags.map(
                    (flag, index) => (
                      <Badge
                        key={index}
                        variant="destructive"
                        className="text-xs"
                      >
                        {flag.replace(/_/g, " ")}
                      </Badge>
                    )
                  )}
                </div>
              </div>
            )}

          {/* Previous Audit Notes */}
          {transaction.audit_metadata.audit_notes && (
            <div>
              <span className="text-sm font-medium">Previous Notes:</span>
              <p className="text-sm text-gray-600 mt-1 bg-gray-50 dark:bg-gray-800 p-2 rounded">
                {transaction.audit_metadata.audit_notes}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Audit Decision Panel */}
      {transaction.audit_metadata.audit_status === "pending" && !submitted && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Audit Decision
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Audit Notes:</label>
              <Textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add notes about your audit decision..."
                className="mt-1"
                rows={3}
              />
            </div>
            <div className="flex gap-3">
              <Button
                onClick={() => handleDecision("approve")}
                disabled={isSubmitting}
                className="flex-1 bg-green-600 hover:bg-green-700"
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Approve
              </Button>
              <Button
                onClick={() => handleDecision("flag")}
                disabled={isSubmitting}
                variant="outline"
                className="flex-1 border-yellow-500 text-yellow-600 hover:bg-yellow-50"
              >
                <AlertTriangle className="h-4 w-4 mr-2" />
                Flag
              </Button>
              <Button
                onClick={() => handleDecision("reject")}
                disabled={isSubmitting}
                variant="outline"
                className="flex-1 border-red-500 text-red-600 hover:bg-red-50"
              >
                <XCircle className="h-4 w-4 mr-2" />
                Reject
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Decision Submitted */}
      {submitted && (
        <Card className="border-green-200 dark:border-green-800 animate-in slide-in-from-top-2 duration-300">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle className="h-5 w-5 animate-pulse" />
              <span className="font-medium">
                Decision submitted successfully!
              </span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
