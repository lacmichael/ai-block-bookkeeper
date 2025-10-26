import { MetricsCards } from "@/components/dashboard/MetricsCards";
import { RevenueExpenseChart } from "@/components/dashboard/RevenueExpenseChart";
import { CashFlowChart } from "@/components/dashboard/CashFlowChart";
import { TransactionsByTypeChart } from "@/components/dashboard/TransactionsByTypeChart";
import { ReconciliationStatusChart } from "@/components/dashboard/ReconciliationStatusChart";
import { TransactionsTable } from "@/components/dashboard/TransactionsTable";
import { getBusinessEvents } from "@/lib/actions/business-events";

export default async function DashboardPage() {
  // Fetch business events from Supabase
  const businessEvents = await getBusinessEvents();

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Financial audit overview
          </p>
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
  );
}
