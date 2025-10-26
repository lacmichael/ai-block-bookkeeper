"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Shield,
  CheckCircle,
  XCircle,
  Clock,
  ExternalLink,
  Copy,
  RefreshCw,
  Hash,
  Calendar,
  DollarSign,
  AlertTriangle,
} from "lucide-react";
import { BusinessEvent } from "@/utils/actions/business-events";
import { AuditMetadata } from "@/utils/mockAuditData";
import { verifyBlockchainRecord } from "@/utils/actions/audit-actions";

interface BlockchainVerificationProps {
  transaction: BusinessEvent & { audit_metadata: AuditMetadata };
}

interface VerificationResult {
  verified: boolean;
  digest?: string;
  blockHeight?: number;
  confirmations?: number;
  error?: string;
}

export function BlockchainVerification({
  transaction,
}: BlockchainVerificationProps) {
  const [verification, setVerification] = useState<VerificationResult | null>(
    null
  );
  const [isVerifying, setIsVerifying] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    // Auto-verify on component mount
    handleVerify();
  }, [transaction.event_id]);

  const handleVerify = async () => {
    setIsVerifying(true);
    try {
      const result = await verifyBlockchainRecord(transaction.event_id);
      setVerification(result);
    } catch (error) {
      console.error("Error verifying blockchain record:", error);
      setVerification({
        verified: false,
        error: "Failed to verify blockchain record",
      });
    } finally {
      setIsVerifying(false);
    }
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

  const getStatusIcon = () => {
    if (isVerifying) {
      return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />;
    }
    if (verification?.verified) {
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    }
    if (verification?.error) {
      return <XCircle className="h-5 w-5 text-red-500" />;
    }
    return <Clock className="h-5 w-5 text-yellow-500" />;
  };

  const getStatusBadge = () => {
    if (isVerifying) {
      return <Badge variant="secondary">Verifying...</Badge>;
    }
    if (verification?.verified) {
      return <Badge variant="success">Verified</Badge>;
    }
    if (verification?.error) {
      return <Badge variant="destructive">Failed</Badge>;
    }
    return <Badge variant="warning">Pending</Badge>;
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

  return (
    <div className="space-y-6">
      {/* Blockchain Verification Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Blockchain Verification
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Verification Status</span>
            <div className="flex items-center gap-2">
              {getStatusIcon()}
              {getStatusBadge()}
            </div>
          </div>

          {verification?.verified && verification.digest && (
            <>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Transaction Hash</span>
                <div className="flex items-center gap-2">
                  <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                    {verification.digest.slice(0, 16)}...
                  </code>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      copyToClipboard(verification.digest!, "hash")
                    }
                  >
                    {copied === "hash" ? (
                      <CheckCircle className="h-4 w-4" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <Hash className="h-4 w-4 text-gray-400" />
                  <div>
                    <div className="text-xs text-gray-500">Block Height</div>
                    <div className="text-sm font-mono">
                      {verification.blockHeight?.toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-gray-400" />
                  <div>
                    <div className="text-xs text-gray-500">Confirmations</div>
                    <div className="text-sm font-mono">
                      {verification.confirmations}
                    </div>
                  </div>
                </div>
              </div>

              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  const explorerUrl = `https://suiexplorer.com/txblock/${verification.digest}`;
                  window.open(explorerUrl, "_blank", "noopener,noreferrer");
                }}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                View on Sui Explorer
              </Button>
            </>
          )}

          {verification?.error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg animate-in slide-in-from-top-2 duration-300">
              <div className="flex items-center gap-2 text-red-600">
                <AlertTriangle className="h-4 w-4 animate-pulse" />
                <span className="text-sm font-medium">Verification Failed</span>
              </div>
              <p className="text-sm text-red-600 mt-1">{verification.error}</p>
            </div>
          )}

          <Button
            variant="outline"
            onClick={handleVerify}
            disabled={isVerifying}
            className="w-full"
          >
            {isVerifying ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Verifying...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                Re-verify
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Transaction Details on Blockchain */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Hash className="h-5 w-5" />
            Blockchain Record
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Amount</span>
              <span className="font-medium">
                {formatCurrency(transaction.amount_minor)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Currency</span>
              <span className="font-medium">{transaction.currency}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Date</span>
              <span className="font-medium">
                {formatDate(transaction.occurred_at)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Type</span>
              <Badge variant="outline">{transaction.event_kind}</Badge>
            </div>
          </div>

          {/* Parties */}
          {(transaction.payer_party || transaction.payee_party) && (
            <div className="pt-4 border-t">
              <h4 className="text-sm font-medium mb-3">Parties</h4>
              <div className="space-y-2">
                {transaction.payer_party && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">From</span>
                    <span className="text-sm font-medium">
                      {transaction.payer_party.display_name}
                    </span>
                  </div>
                )}
                {transaction.payee_party && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">To</span>
                    <span className="text-sm font-medium">
                      {transaction.payee_party.display_name}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Immutability Proof */}
          {verification?.verified && (
            <div className="pt-4 border-t">
              <div className="flex items-center gap-2 text-green-600">
                <Shield className="h-4 w-4" />
                <span className="text-sm font-medium">Immutable Record</span>
              </div>
              <p className="text-xs text-gray-600 mt-1">
                This transaction has been permanently recorded on the Sui
                blockchain and cannot be modified.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
