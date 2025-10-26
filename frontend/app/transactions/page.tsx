"use client";

import { useState, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Search,
  ArrowUpDown,
  Calendar,
  DollarSign,
  FileText,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Clock,
  AlertCircle,
  Eye,
  ArrowRight,
  Hash,
  Users,
  Building,
  CreditCard,
  RefreshCw,
  Shield,
} from "lucide-react";
import Link from "next/link";
import {
  getBusinessEvents,
  BusinessEvent,
} from "@/utils/actions/business-events";
import { useEffect } from "react";

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<BusinessEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [sortBy, setSortBy] = useState("date");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const data = await getBusinessEvents();
        setTransactions(data);
      } catch (error) {
        console.error("Error fetching transactions:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, []);

  const filteredAndSortedTransactions = useMemo(() => {
    const filtered = transactions.filter((transaction) => {
      const matchesSearch =
        transaction.description
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        transaction.event_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        transaction.source_id
          .toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        transaction.payer_party?.display_name
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        transaction.payee_party?.display_name
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase());

      const matchesType =
        filterType === "all" || transaction.event_kind === filterType;
      const matchesStatus =
        filterStatus === "all" ||
        transaction.reconciliation_state === filterStatus;

      return matchesSearch && matchesType && matchesStatus;
    });

    filtered.sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case "date":
          comparison =
            new Date(a.occurred_at).getTime() -
            new Date(b.occurred_at).getTime();
          break;
        case "amount":
          comparison = a.amount_minor - b.amount_minor;
          break;
        case "type":
          comparison = a.event_kind.localeCompare(b.event_kind);
          break;
        case "status":
          comparison = a.reconciliation_state.localeCompare(
            b.reconciliation_state
          );
          break;
        default:
          comparison = 0;
      }

      return sortOrder === "asc" ? comparison : -comparison;
    });

    return filtered;
  }, [transactions, searchTerm, filterType, filterStatus, sortBy, sortOrder]);

  // Pagination logic
  const totalPages = Math.ceil(
    filteredAndSortedTransactions.length / itemsPerPage
  );
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedTransactions = filteredAndSortedTransactions.slice(
    startIndex,
    endIndex
  );

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, filterType, filterStatus, sortBy, sortOrder]);

  const getEventKindBadge = (kind: string) => {
    switch (kind) {
      case "INVOICE_RECEIVED":
        return (
          <Badge variant="info" className="flex items-center gap-1">
            <FileText className="h-3 w-3" />
            Invoice
          </Badge>
        );
      case "BANK_POSTED":
        return (
          <Badge variant="secondary" className="flex items-center gap-1">
            <CreditCard className="h-3 w-3" />
            Bank
          </Badge>
        );
      case "PAYMENT_SENT":
        return (
          <Badge variant="outline" className="flex items-center gap-1">
            <ArrowRight className="h-3 w-3" />
            Payment
          </Badge>
        );
      case "REFUND":
        return (
          <Badge variant="warning" className="flex items-center gap-1">
            <RefreshCw className="h-3 w-3" />
            Refund
          </Badge>
        );
      case "ADJUSTMENT":
        return (
          <Badge variant="secondary" className="flex items-center gap-1">
            <ArrowUpDown className="h-3 w-3" />
            Adjustment
          </Badge>
        );
      default:
        return <Badge variant="secondary">{kind}</Badge>;
    }
  };

  const getStatusBadge = (state: string) => {
    switch (state) {
      case "RECONCILED":
        return (
          <Badge variant="success" className="flex items-center gap-1">
            <CheckCircle className="h-3 w-3" />
            Reconciled
          </Badge>
        );
      case "UNRECONCILED":
        return (
          <Badge variant="destructive" className="flex items-center gap-1">
            <AlertCircle className="h-3 w-3" />
            Unreconciled
          </Badge>
        );
      case "PARTIAL":
        return (
          <Badge variant="warning" className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            Partial
          </Badge>
        );
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
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getAmountIcon = (amount: number) => {
    return amount >= 0 ? (
      <TrendingUp className="h-4 w-4 text-green-500" />
    ) : (
      <TrendingDown className="h-4 w-4 text-red-500" />
    );
  };

  const getPartyIcon = (role: string | null) => {
    switch (role) {
      case "CUSTOMER":
        return <Users className="h-4 w-4 text-blue-500" />;
      case "VENDOR":
        return <Building className="h-4 w-4 text-orange-500" />;
      case "EMPLOYEE":
        return <Users className="h-4 w-4 text-purple-500" />;
      case "INTERNAL":
        return <Building className="h-4 w-4 text-gray-500" />;
      default:
        return <Users className="h-4 w-4 text-gray-400" />;
    }
  };

  // Calculate summary statistics
  const totalRevenue = transactions
    .filter((t) => t.amount_minor > 0)
    .reduce((sum, t) => sum + t.amount_minor, 0);

  const totalExpenses = Math.abs(
    transactions
      .filter((t) => t.amount_minor < 0)
      .reduce((sum, t) => sum + t.amount_minor, 0)
  );

  const reconciledCount = transactions.filter(
    (t) => t.reconciliation_state === "RECONCILED"
  ).length;
  const reconciliationRate =
    transactions.length > 0 ? (reconciledCount / transactions.length) * 100 : 0;

  if (loading) {
    return (
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="flex items-center gap-2">
              <RefreshCw className="h-6 w-6 animate-spin" />
              <span className="text-lg">Loading transactions...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Transactions
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            View and manage all financial transactions across your business
          </p>
        </div>

        {/* Summary Statistics */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Total Revenue
                  </p>
                  <p className="text-2xl font-bold text-green-600">
                    {formatCurrency(totalRevenue)}
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Total Expenses
                  </p>
                  <p className="text-2xl font-bold text-red-600">
                    {formatCurrency(totalExpenses)}
                  </p>
                </div>
                <TrendingDown className="h-8 w-8 text-red-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Net Profit
                  </p>
                  <p
                    className={`text-2xl font-bold ${
                      totalRevenue - totalExpenses >= 0
                        ? "text-green-600"
                        : "text-red-600"
                    }`}
                  >
                    {formatCurrency(totalRevenue - totalExpenses)}
                  </p>
                </div>
                <DollarSign className="h-8 w-8 text-blue-500" />
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
                    {reconciliationRate.toFixed(1)}%
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters and Search */}
        <Card className="mb-6">
          <CardContent className="p-4 md:p-6">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search transactions, parties, or descriptions..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-2">
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-sm"
                >
                  <option value="all">All Types</option>
                  <option value="INVOICE_RECEIVED">Invoices</option>
                  <option value="BANK_POSTED">Bank Transactions</option>
                  <option value="PAYMENT_SENT">Payments</option>
                  <option value="REFUND">Refunds</option>
                  <option value="ADJUSTMENT">Adjustments</option>
                </select>

                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-sm"
                >
                  <option value="all">All Status</option>
                  <option value="RECONCILED">Reconciled</option>
                  <option value="UNRECONCILED">Unreconciled</option>
                  <option value="PARTIAL">Partial</option>
                </select>

                <select
                  value={`${sortBy}-${sortOrder}`}
                  onChange={(e) => {
                    const [field, order] = e.target.value.split("-");
                    setSortBy(field);
                    setSortOrder(order as "asc" | "desc");
                  }}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-sm"
                >
                  <option value="date-desc">Date (Newest)</option>
                  <option value="date-asc">Date (Oldest)</option>
                  <option value="amount-desc">Amount (High to Low)</option>
                  <option value="amount-asc">Amount (Low to High)</option>
                  <option value="type-asc">Type (A-Z)</option>
                  <option value="status-asc">Status (A-Z)</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Transactions List */}
        <div className="space-y-4">
          {paginatedTransactions.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No transactions found
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {searchTerm || filterType !== "all" || filterStatus !== "all"
                    ? "Try adjusting your search or filter criteria."
                    : "No transactions have been recorded yet."}
                </p>
              </CardContent>
            </Card>
          ) : (
            paginatedTransactions.map((transaction) => (
              <Card
                key={transaction.event_id}
                className="hover:shadow-lg transition-shadow duration-200"
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-3">
                        {getAmountIcon(transaction.amount_minor)}
                        <div className="flex-1 min-w-0">
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                            {transaction.description ||
                              `Transaction ${transaction.event_id.slice(0, 8)}`}
                          </h3>
                          <div className="flex items-center gap-2 mt-1">
                            {getEventKindBadge(transaction.event_kind)}
                            {getStatusBadge(transaction.reconciliation_state)}
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-600 dark:text-gray-400">
                            {formatDate(transaction.occurred_at)}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          <Hash className="h-4 w-4 text-gray-400" />
                          <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                            {transaction.event_id.slice(0, 12)}...
                          </code>
                        </div>

                        <div className="flex items-center gap-2">
                          <span className="text-gray-600 dark:text-gray-400">
                            Source:
                          </span>
                          <Badge variant="outline">
                            {transaction.source_system}
                          </Badge>
                        </div>
                      </div>

                      {/* Parties */}
                      <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 mt-4">
                        {transaction.payer_party && (
                          <div className="flex items-center gap-2">
                            {getPartyIcon(transaction.payer_role)}
                            <div>
                              <div className="text-sm font-medium text-gray-900 dark:text-white">
                                {transaction.payer_party.display_name}
                              </div>
                              <div className="text-xs text-gray-500">
                                {transaction.payer_role} (Payer)
                              </div>
                            </div>
                          </div>
                        )}

                        {transaction.payer_party && transaction.payee_party && (
                          <ArrowRight className="h-4 w-4 text-gray-400 hidden sm:block" />
                        )}

                        {transaction.payee_party && (
                          <div className="flex items-center gap-2">
                            {getPartyIcon(transaction.payee_role)}
                            <div>
                              <div className="text-sm font-medium text-gray-900 dark:text-white">
                                {transaction.payee_party.display_name}
                              </div>
                              <div className="text-xs text-gray-500">
                                {transaction.payee_role} (Payee)
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col items-end gap-3 mt-4 sm:mt-0 sm:ml-6">
                      <div className="text-right">
                        <div
                          className={`text-2xl font-bold ${
                            transaction.amount_minor >= 0
                              ? "text-green-600"
                              : "text-red-600"
                          }`}
                        >
                          {formatCurrency(transaction.amount_minor)}
                        </div>
                        <div className="text-sm text-gray-500">
                          {transaction.currency}
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Link href={`/transactions/${transaction.event_id}`}>
                          <Button
                            variant="outline"
                            size="sm"
                            className="flex items-center gap-2"
                          >
                            <Eye className="h-4 w-4" />
                            View Details
                          </Button>
                        </Link>
                        <Link
                          href={`/audit/transaction/${transaction.event_id}`}
                        >
                          <Button
                            variant="outline"
                            size="sm"
                            className="flex items-center gap-2"
                          >
                            <Shield className="h-4 w-4" />
                            Audit
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <Card className="mt-6">
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Showing {startIndex + 1} to{" "}
                  {Math.min(endIndex, filteredAndSortedTransactions.length)} of{" "}
                  {filteredAndSortedTransactions.length} transactions
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      setCurrentPage((prev) => Math.max(prev - 1, 1))
                    }
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>

                  <div className="flex items-center gap-1">
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum;
                      if (totalPages <= 5) {
                        pageNum = i + 1;
                      } else if (currentPage <= 3) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = currentPage - 2 + i;
                      }

                      return (
                        <Button
                          key={pageNum}
                          variant={
                            currentPage === pageNum ? "default" : "outline"
                          }
                          size="sm"
                          onClick={() => setCurrentPage(pageNum)}
                          className="w-8 h-8 p-0"
                        >
                          {pageNum}
                        </Button>
                      );
                    })}
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      setCurrentPage((prev) => Math.min(prev + 1, totalPages))
                    }
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Summary */}
        {filteredAndSortedTransactions.length > 0 && totalPages <= 1 && (
          <div className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
            Showing {filteredAndSortedTransactions.length} of{" "}
            {transactions.length} transactions
          </div>
        )}
      </div>
    </div>
  );
}
