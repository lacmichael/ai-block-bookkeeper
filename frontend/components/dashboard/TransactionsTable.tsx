"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";
import { formatCurrency } from "@/utils/mockData";
import { BusinessEvent } from "@/utils/actions/business-events";
import { PartyInfo } from "./PartyInfo";
import Link from "next/link";

interface TransactionsTableProps {
  businessEvents: BusinessEvent[];
}

type SortField =
  | "occurred_at"
  | "description"
  | "event_kind"
  | "amount_minor"
  | "reconciliation_state"
  | "source_system"
  | "dedupe_key";
type SortDirection = "asc" | "desc";

export function TransactionsTable({ businessEvents }: TransactionsTableProps) {
  const [sortField, setSortField] = useState<SortField>("occurred_at");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const sortedTransactions = [...businessEvents].sort((a, b) => {
    let aValue: any = a[sortField];
    let bValue: any = b[sortField];

    if (sortField === "occurred_at") {
      aValue = new Date(aValue).getTime();
      bValue = new Date(bValue).getTime();
    }

    if (sortDirection === "asc") {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

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

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="h-4 w-4" />;
    }
    return sortDirection === "asc" ? (
      <ArrowUp className="h-4 w-4" />
    ) : (
      <ArrowDown className="h-4 w-4" />
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Transactions</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort("occurred_at")}
                  className="h-auto p-0 font-medium"
                >
                  Date {getSortIcon("occurred_at")}
                </Button>
              </TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort("description")}
                  className="h-auto p-0 font-medium"
                >
                  Description {getSortIcon("description")}
                </Button>
              </TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort("event_kind")}
                  className="h-auto p-0 font-medium"
                >
                  Type {getSortIcon("event_kind")}
                </Button>
              </TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort("amount_minor")}
                  className="h-auto p-0 font-medium"
                >
                  Amount {getSortIcon("amount_minor")}
                </Button>
              </TableHead>
              <TableHead>Payer</TableHead>
              <TableHead>Payee</TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort("source_system")}
                  className="h-auto p-0 font-medium"
                >
                  Source {getSortIcon("source_system")}
                </Button>
              </TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort("reconciliation_state")}
                  className="h-auto p-0 font-medium"
                >
                  Status {getSortIcon("reconciliation_state")}
                </Button>
              </TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedTransactions.map((transaction) => (
              <TableRow key={transaction.event_id}>
                <TableCell className="font-medium">
                  {formatDate(transaction.occurred_at)}
                </TableCell>
                <TableCell className="max-w-[200px] truncate">
                  <div>
                    <div className="truncate">{transaction.description}</div>
                    <div className="text-xs text-muted-foreground">
                      Ref: {transaction.source_id}
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  {getEventKindBadge(transaction.event_kind)}
                </TableCell>
                <TableCell
                  className={`font-medium ${
                    transaction.amount_minor >= 0
                      ? "text-green-600"
                      : "text-red-600"
                  }`}
                >
                  {formatCurrency(transaction.amount_minor)}
                </TableCell>
                <TableCell>
                  <PartyInfo
                    party={transaction.payer_party || null}
                    role={transaction.payer_role || undefined}
                  >
                    <div className="text-sm">
                      {transaction.payer_party?.display_name || "-"}
                    </div>
                    {transaction.payer_role && (
                      <div className="text-xs text-muted-foreground">
                        {transaction.payer_role}
                      </div>
                    )}
                  </PartyInfo>
                </TableCell>
                <TableCell>
                  <PartyInfo
                    party={transaction.payee_party || null}
                    role={transaction.payee_role || undefined}
                  >
                    <div className="text-sm">
                      {transaction.payee_party?.display_name || "-"}
                    </div>
                    {transaction.payee_role && (
                      <div className="text-xs text-muted-foreground">
                        {transaction.payee_role}
                      </div>
                    )}
                  </PartyInfo>
                </TableCell>
                <TableCell>
                  <Badge variant="outline">{transaction.source_system}</Badge>
                </TableCell>
                <TableCell>
                  {getStatusBadge(transaction.reconciliation_state)}
                </TableCell>
                <TableCell>
                  <Link href={`/transactions/${transaction.event_id}`}>
                    <Button variant="outline" size="sm">
                      View
                    </Button>
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
