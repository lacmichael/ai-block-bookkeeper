"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Copy,
  CheckCircle,
  Calendar,
  DollarSign,
  FileText,
  Hash,
} from "lucide-react";
import { BusinessEvent } from "@/utils/actions/business-events";
import { useState } from "react";

interface TransactionDetailsProps {
  transaction: BusinessEvent;
}

export function TransactionDetails({ transaction }: TransactionDetailsProps) {
  const [copied, setCopied] = useState<string | null>(null);

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(label);
      setTimeout(() => setCopied(null), 2000);
    } catch (err) {
      console.error("Failed to copy: ", err);
    }
  };

  const getEventKindBadge = (kind: string) => {
    switch (kind) {
      case "INVOICE_RECEIVED":
        return <Badge variant="info">Invoice</Badge>;
      case "BANK_POSTED":
        return <Badge variant="secondary">Bank</Badge>;
      case "PAYMENT_SENT":
        return <Badge variant="outline">Payment</Badge>;
      case "REFUND":
        return <Badge variant="warning">Refund</Badge>;
      case "ADJUSTMENT":
        return <Badge variant="secondary">Adjustment</Badge>;
      default:
        return <Badge variant="secondary">{kind}</Badge>;
    }
  };

  const getStatusBadge = (state: string) => {
    switch (state) {
      case "RECONCILED":
        return <Badge variant="success">Reconciled</Badge>;
      case "UNRECONCILED":
        return <Badge variant="destructive">Unreconciled</Badge>;
      case "PARTIAL":
        return <Badge variant="warning">Partial</Badge>;
      default:
        return <Badge variant="secondary">{state}</Badge>;
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
      month: "long",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Transaction Information
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Event ID */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium flex items-center gap-2">
            <Hash className="h-4 w-4" />
            Event ID
          </span>
          <div className="flex items-center gap-2">
            <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
              {transaction.event_id.slice(0, 16)}...
            </code>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(transaction.event_id, "eventId")}
            >
              {copied === "eventId" ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Description */}
        <div>
          <span className="text-sm font-medium">Description</span>
          <div className="text-sm text-muted-foreground mt-1">
            {transaction.description || "No description provided"}
          </div>
        </div>

        {/* Amount */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium flex items-center gap-2">
            <DollarSign className="h-4 w-4" />
            Amount
          </span>
          <div
            className={`text-lg font-bold ${
              transaction.amount_minor >= 0 ? "text-green-600" : "text-red-600"
            }`}
          >
            {formatCurrency(transaction.amount_minor)}
          </div>
        </div>

        {/* Event Type */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Type</span>
          {getEventKindBadge(transaction.event_kind)}
        </div>

        {/* Status */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Status</span>
          {getStatusBadge(transaction.reconciliation_state)}
        </div>

        {/* Source System */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Source</span>
          <Badge variant="outline">{transaction.source_system}</Badge>
        </div>

        {/* Source ID */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Source ID</span>
          <div className="flex items-center gap-2">
            <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
              {transaction.source_id}
            </code>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(transaction.source_id, "sourceId")}
            >
              {copied === "sourceId" ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Occurred At */}
        <div>
          <span className="text-sm font-medium flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Occurred At
          </span>
          <div className="text-sm text-muted-foreground mt-1">
            {formatDate(transaction.occurred_at)}
          </div>
        </div>

        {/* Recorded At */}
        <div>
          <span className="text-sm font-medium">Recorded At</span>
          <div className="text-sm text-muted-foreground mt-1">
            {formatDate(transaction.recorded_at)}
          </div>
        </div>

        {/* Dedupe Key */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Dedupe Key</span>
          <div className="flex items-center gap-2">
            <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
              {transaction.dedupe_key.slice(0, 16)}...
            </code>
            <Button
              variant="ghost"
              size="sm"
              onClick={() =>
                copyToClipboard(transaction.dedupe_key, "dedupeKey")
              }
            >
              {copied === "dedupeKey" ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Processing State */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Processing State</span>
          <Badge
            variant={
              transaction.processing.state === "COMPLETED"
                ? "success"
                : "warning"
            }
          >
            {transaction.processing.state}
          </Badge>
        </div>

        {/* Processing Error */}
        {transaction.processing.last_error && (
          <div>
            <span className="text-sm font-medium text-red-600">Last Error</span>
            <div className="text-sm text-red-600 mt-1 bg-red-50 dark:bg-red-900/20 p-2 rounded">
              {transaction.processing.last_error}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
