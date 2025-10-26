import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { Button } from "@/components/ui/button";
import { signOut } from "../login/actions";
import { MetricsCards } from "@/components/dashboard/MetricsCards";
import { RevenueExpenseChart } from "@/components/dashboard/RevenueExpenseChart";
import { CashFlowChart } from "@/components/dashboard/CashFlowChart";
import { TransactionsByTypeChart } from "@/components/dashboard/TransactionsByTypeChart";
import { ReconciliationStatusChart } from "@/components/dashboard/ReconciliationStatusChart";
import { TransactionsTable } from "@/components/dashboard/TransactionsTable";
import { getBusinessEvents } from "@/lib/actions/business-events";

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // If user is not authenticated, redirect to login
  if (!user) {
    redirect("/login");
  }

  // Fetch business events from Supabase
  const businessEvents = await getBusinessEvents();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                AI Block Bookkeeper
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Financial audit dashboard
              </p>
            </div>
            <form action={signOut}>
              <Button variant="outline" type="submit">
                Sign Out
              </Button>
            </form>
          </div>

          {/* Metrics Cards */}
          <div className="mb-8">
            <MetricsCards />
          </div>

          {/* Charts Grid */}
          <div className="grid gap-6 mb-8">
            <div className="grid gap-6 md:grid-cols-2">
              <RevenueExpenseChart />
              <CashFlowChart />
            </div>
            <div className="grid gap-6 md:grid-cols-2">
              <TransactionsByTypeChart />
              <ReconciliationStatusChart />
            </div>
          </div>

          {/* Transactions Table */}
          <TransactionsTable businessEvents={businessEvents} />
        </div>
      </div>
    </div>
  );
}
