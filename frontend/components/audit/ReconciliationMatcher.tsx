"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ArrowRight,
  CheckCircle,
  XCircle,
  RefreshCw,
  DollarSign,
  Calendar,
  Building,
  FileText,
  CreditCard,
  Link,
  AlertTriangle,
} from "lucide-react";
import {
  getReconciliationCandidates,
  submitReconciliation,
  ReconciliationCandidate,
} from "@/utils/actions/audit-actions";

interface SuggestedMatch {
  invoice: ReconciliationCandidate;
  bankRecord: ReconciliationCandidate;
  confidence: number;
}

export function ReconciliationMatcher() {
  const [invoices, setInvoices] = useState<ReconciliationCandidate[]>([]);
  const [bankRecords, setBankRecords] = useState<ReconciliationCandidate[]>([]);
  const [suggestedMatches, setSuggestedMatches] = useState<SuggestedMatch[]>(
    []
  );
  const [selectedMatches, setSelectedMatches] = useState<Set<string>>(
    new Set()
  );
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const data = await getReconciliationCandidates();
      setInvoices(data.invoices);
      setBankRecords(data.bankRecords);
      setSuggestedMatches(data.suggestedMatches);
    } catch (error) {
      console.error("Error fetching reconciliation data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleMatch = (invoiceId: string, bankRecordId: string) => {
    const matchKey = `${invoiceId}-${bankRecordId}`;
    setSelectedMatches((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(matchKey)) {
        newSet.delete(matchKey);
      } else {
        newSet.add(matchKey);
      }
      return newSet;
    });
  };

  const handleSubmitMatches = async () => {
    setIsSubmitting(true);
    try {
      const matches = Array.from(selectedMatches);
      for (const match of matches) {
        const [invoiceId, bankRecordId] = match.split("-");
        await submitReconciliation(invoiceId, bankRecordId);
      }
      // Refresh data after submission
      await fetchData();
      setSelectedMatches(new Set());
    } catch (error) {
      console.error("Error submitting matches:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return "text-green-600";
    if (confidence >= 70) return "text-yellow-600";
    return "text-red-600";
  };

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 90) return <Badge variant="success">{confidence}%</Badge>;
    if (confidence >= 70) return <Badge variant="warning">{confidence}%</Badge>;
    return <Badge variant="destructive">{confidence}%</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span className="text-lg">Loading reconciliation data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">{invoices.length}</div>
                <div className="text-sm text-gray-600">Unmatched Invoices</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <CreditCard className="h-5 w-5 text-green-500" />
              <div>
                <div className="text-2xl font-bold">{bankRecords.length}</div>
                <div className="text-sm text-gray-600">
                  Unmatched Bank Records
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Link className="h-5 w-5 text-purple-500" />
              <div>
                <div className="text-2xl font-bold">
                  {suggestedMatches.length}
                </div>
                <div className="text-sm text-gray-600">Suggested Matches</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Suggested Matches */}
      {suggestedMatches.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5" />
              Suggested Matches
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {suggestedMatches.map((match, index) => {
                const matchKey = `${match.invoice.id}-${match.bankRecord.id}`;
                const isSelected = selectedMatches.has(matchKey);

                return (
                  <div
                    key={index}
                    className={`p-4 border rounded-lg cursor-pointer transition-all duration-200 hover:scale-[1.01] ${
                      isSelected
                        ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md"
                        : "border-gray-200 hover:border-gray-300 hover:shadow-sm"
                    }`}
                    onClick={() =>
                      handleMatch(match.invoice.id, match.bankRecord.id)
                    }
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() =>
                            handleMatch(match.invoice.id, match.bankRecord.id)
                          }
                          className="rounded"
                        />
                        <span className="font-medium">Match #{index + 1}</span>
                      </div>
                      {getConfidenceBadge(match.confidence)}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Invoice */}
                      <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded">
                        <div className="flex items-center gap-2 mb-2">
                          <FileText className="h-4 w-4 text-blue-500" />
                          <span className="text-sm font-medium">Invoice</span>
                        </div>
                        <div className="space-y-1 text-sm">
                          <div className="flex items-center gap-2">
                            <DollarSign className="h-3 w-3 text-gray-400" />
                            <span className="font-medium">
                              {formatCurrency(match.invoice.amount)}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Calendar className="h-3 w-3 text-gray-400" />
                            <span>{formatDate(match.invoice.date)}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Building className="h-3 w-3 text-gray-400" />
                            <span>{match.invoice.party_name}</span>
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {match.invoice.description}
                          </div>
                        </div>
                      </div>

                      {/* Arrow */}
                      <div className="flex items-center justify-center">
                        <ArrowRight className="h-6 w-6 text-gray-400" />
                      </div>

                      {/* Bank Record */}
                      <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded">
                        <div className="flex items-center gap-2 mb-2">
                          <CreditCard className="h-4 w-4 text-green-500" />
                          <span className="text-sm font-medium">
                            Bank Record
                          </span>
                        </div>
                        <div className="space-y-1 text-sm">
                          <div className="flex items-center gap-2">
                            <DollarSign className="h-3 w-3 text-gray-400" />
                            <span className="font-medium">
                              {formatCurrency(match.bankRecord.amount)}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Calendar className="h-3 w-3 text-gray-400" />
                            <span>{formatDate(match.bankRecord.date)}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Building className="h-3 w-3 text-gray-400" />
                            <span>{match.bankRecord.party_name}</span>
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {match.bankRecord.description}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {selectedMatches.size > 0 && (
              <div className="mt-6 flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-blue-600" />
                  <span className="font-medium">
                    {selectedMatches.size} match
                    {selectedMatches.size !== 1 ? "es" : ""} selected
                  </span>
                </div>
                <Button
                  onClick={handleSubmitMatches}
                  disabled={isSubmitting}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {isSubmitting ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Link className="h-4 w-4 mr-2" />
                      Submit Matches
                    </>
                  )}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Manual Matching */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Unmatched Invoices */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Unmatched Invoices
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {invoices.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  No unmatched invoices
                </p>
              ) : (
                invoices.map((invoice) => (
                  <div key={invoice.id} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{invoice.party_name}</span>
                      <span className="text-lg font-bold">
                        {formatCurrency(invoice.amount)}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      {formatDate(invoice.date)} • {invoice.description}
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Unmatched Bank Records */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              Unmatched Bank Records
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {bankRecords.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  No unmatched bank records
                </p>
              ) : (
                bankRecords.map((record) => (
                  <div key={record.id} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{record.party_name}</span>
                      <span className="text-lg font-bold">
                        {formatCurrency(record.amount)}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      {formatDate(record.date)} • {record.description}
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Instructions */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-blue-500 mt-0.5" />
            <div>
              <h4 className="font-medium mb-2">How to Reconcile</h4>
              <ol className="text-sm text-gray-600 space-y-1 list-decimal list-inside">
                <li>
                  Review the suggested matches above and select the ones that
                  look correct
                </li>
                <li>
                  For manual matching, drag invoices to bank records or vice
                  versa
                </li>
                <li>
                  Verify amounts, dates, and party names match before confirming
                </li>
                <li>Click "Submit Matches" to finalize the reconciliation</li>
              </ol>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
