import { notFound } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { getBusinessEventById } from "@/utils/actions/business-events";
import { SuiLedgerVisualization } from "@/components/transactions/SuiLedgerVisualization";
import { TransactionDetails } from "@/components/transactions/TransactionDetails";
import { PartyInfo } from "@/components/dashboard/PartyInfo";

interface TransactionDetailPageProps {
  params: {
    id: string;
  };
}

export default async function TransactionDetailPage({
  params,
}: TransactionDetailPageProps) {
  const { id } = await params;
  const transaction = await getBusinessEventById(id);

  if (!transaction) {
    notFound();
  }

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Navigation Buttons */}
        <div className="mb-6">
          <div className="flex gap-3">
            <Link href="/transactions">
              <Button variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Transactions
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Transaction Information */}
          <div className="space-y-6">
            <TransactionDetails transaction={transaction} />

            {/* Parties Information */}
            <Card>
              <CardHeader>
                <CardTitle>Parties Involved</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-medium text-sm text-gray-500 mb-2">
                    Payer
                  </h4>
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
                </div>

                <div>
                  <h4 className="font-medium text-sm text-gray-500 mb-2">
                    Payee
                  </h4>
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
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sui Blockchain Visualization */}
          <div>
            <SuiLedgerVisualization transaction={transaction} />
          </div>
        </div>
      </div>
    </div>
  );
}
