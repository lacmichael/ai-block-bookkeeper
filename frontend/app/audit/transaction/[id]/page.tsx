import { notFound } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { getBusinessEventById } from "@/utils/actions/business-events";
import { TransactionAuditCard } from "@/components/audit/TransactionAuditCard";
import { AuditTrail } from "@/components/audit/AuditTrail";
import { BlockchainVerification } from "@/components/audit/BlockchainVerification";

interface TransactionAuditPageProps {
  params: {
    id: string;
  };
}

export default async function TransactionAuditPage({
  params,
}: TransactionAuditPageProps) {
  const { id } = await params;
  const transaction = await getBusinessEventById(id);

  if (!transaction) {
    notFound();
  }

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Back Button */}
        <div className="mb-6">
          <Link href="/audit">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Audit Dashboard
            </Button>
          </Link>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Audit Decision Panel */}
          <div className="space-y-6">
            <TransactionAuditCard transaction={transaction} />
            <AuditTrail transaction={transaction} />
          </div>

          {/* Blockchain Verification */}
          <div>
            <BlockchainVerification transaction={transaction} />
          </div>
        </div>
      </div>
    </div>
  );
}
