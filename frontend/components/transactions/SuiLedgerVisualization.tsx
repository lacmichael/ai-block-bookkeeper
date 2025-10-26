"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ExternalLink,
  Copy,
  CheckCircle,
  Clock,
  AlertCircle,
  ArrowRight,
  Shield,
  Hash,
  Calendar,
  DollarSign,
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { BusinessEvent } from "@/utils/actions/business-events";

interface SuiLedgerVisualizationProps {
  transaction: BusinessEvent;
}

interface SuiTransaction {
  digest: string;
  timestamp: string;
  status: "success" | "pending" | "failed";
  gasUsed: number;
  gasPrice: number;
  sender: string;
  recipient: string;
  amount: number;
  currency: string;
  blockHeight: number;
  epoch: number;
  events: SuiEvent[];
}

interface SuiEvent {
  type: string;
  description: string;
  timestamp: string;
  data: Record<string, any>;
}

export function SuiLedgerVisualization({
  transaction,
}: SuiLedgerVisualizationProps) {
  const [copied, setCopied] = useState<string | null>(null);

  // Generate a deterministic digest based on transaction data
  const generateDigest = (
    eventId: string,
    amount: number,
    timestamp: string
  ): string => {
    // Create a simple hash-like string based on transaction data
    const data = `${eventId}-${amount}-${timestamp}`;
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      const char = data.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    // Convert to hex and pad to 64 characters
    const hex = Math.abs(hash).toString(16).padStart(8, "0");
    return `0x${hex.repeat(8)}`;
  };

  // Mock Sui transaction data based on the business event
  const suiTransaction: SuiTransaction = {
    digest: generateDigest(
      transaction.event_id,
      transaction.amount_minor,
      transaction.occurred_at
    ),
    timestamp: transaction.occurred_at,
    status: "success",
    gasUsed: Math.floor(Math.random() * 1000) + 100,
    gasPrice: 1000,
    sender:
      transaction.payer_party?.sui_address ||
      `0x${Math.random().toString(16).substr(2, 40)}`,
    recipient:
      transaction.payee_party?.sui_address ||
      `0x${Math.random().toString(16).substr(2, 40)}`,
    amount: Math.abs(transaction.amount_minor),
    currency: transaction.currency,
    blockHeight: Math.floor(Math.random() * 1000000) + 50000000,
    epoch: Math.floor(Math.random() * 100) + 1000,
    events: [
      {
        type: "Transfer",
        description: "Token transfer initiated",
        timestamp: transaction.occurred_at,
        data: {
          from: transaction.payer_party?.sui_address,
          to: transaction.payee_party?.sui_address,
          amount: Math.abs(transaction.amount_minor),
          currency: transaction.currency,
        },
      },
      {
        type: "BalanceUpdate",
        description: "Account balances updated",
        timestamp: new Date(
          new Date(transaction.occurred_at).getTime() + 1000
        ).toISOString(),
        data: {
          payer_balance: Math.floor(Math.random() * 100000),
          payee_balance: Math.floor(Math.random() * 100000),
        },
      },
      {
        type: "AuditTrail",
        description: "Transaction recorded in audit trail",
        timestamp: new Date(
          new Date(transaction.occurred_at).getTime() + 2000
        ).toISOString(),
        data: {
          event_id: transaction.event_id,
          source_system: transaction.source_system,
          reconciliation_state: transaction.reconciliation_state,
        },
      },
    ],
  };

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(label);
      setTimeout(() => setCopied(null), 2000);
    } catch (err) {
      console.error("Failed to copy: ", err);
    }
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
        return <Badge variant="success">Confirmed</Badge>;
      case "pending":
        return <Badge variant="warning">Pending</Badge>;
      case "failed":
        return <Badge variant="destructive">Failed</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Transaction Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Sui Blockchain Record
          </CardTitle>
          <p className="text-xs text-muted-foreground mt-1">
            * This is a simulated blockchain record for demonstration purposes
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Transaction Hash</span>
            <div className="flex items-center gap-2">
              <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                {suiTransaction.digest.slice(0, 16)}...
              </code>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => copyToClipboard(suiTransaction.digest, "hash")}
              >
                {copied === "hash" ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Status</span>
            <div className="flex items-center gap-2">
              {getStatusIcon(suiTransaction.status)}
              {getStatusBadge(suiTransaction.status)}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Block Height</span>
            <span className="text-sm font-mono">
              {suiTransaction.blockHeight.toLocaleString()}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Epoch</span>
            <span className="text-sm font-mono">{suiTransaction.epoch}</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Gas Used</span>
            <span className="text-sm font-mono">
              {suiTransaction.gasUsed} SUI
            </span>
          </div>

          <div className="pt-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    onClick={() => {
                      // Construct the Sui Explorer URL
                      const digest = suiTransaction.digest;
                      const explorerUrl = `https://suiexplorer.com/txblock/${digest}`;

                      // Open in new tab with security attributes
                      window.open(explorerUrl, "_blank", "noopener,noreferrer");
                    }}
                    disabled={!suiTransaction.digest}
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View on Sui Explorer
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>
                    View this simulated transaction on the Sui blockchain
                    explorer (demo mode)
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </CardContent>
      </Card>

      {/* Transaction Flow */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ArrowRight className="h-5 w-5" />
            Transaction Flow
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Sender */}
            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div>
                <div className="font-medium text-sm">From</div>
                <div className="text-xs text-muted-foreground font-mono">
                  {suiTransaction.sender.slice(0, 20)}...
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium">
                  -{suiTransaction.amount.toLocaleString()}{" "}
                  {suiTransaction.currency}
                </div>
                <div className="text-xs text-red-500">Debit</div>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex justify-center">
              <ArrowRight className="h-6 w-6 text-gray-400" />
            </div>

            {/* Recipient */}
            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div>
                <div className="font-medium text-sm">To</div>
                <div className="text-xs text-muted-foreground font-mono">
                  {suiTransaction.recipient.slice(0, 20)}...
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium">
                  +{suiTransaction.amount.toLocaleString()}{" "}
                  {suiTransaction.currency}
                </div>
                <div className="text-xs text-green-500">Credit</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Event Timeline */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Hash className="h-5 w-5" />
            Event Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {suiTransaction.events.map((event, index) => (
              <div key={index} className="flex items-start gap-3">
                <div className="shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <div className="font-medium text-sm">{event.type}</div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {event.description}
                  </div>
                  {Object.keys(event.data).length > 0 && (
                    <details className="mt-2">
                      <summary className="text-xs text-blue-600 cursor-pointer">
                        View Details
                      </summary>
                      <pre className="text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded mt-1 overflow-x-auto">
                        {JSON.stringify(event.data, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
