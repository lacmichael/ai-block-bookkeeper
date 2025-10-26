import { AuditDashboard } from "@/components/audit/AuditDashboard";

export default function AuditPage() {
  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Audit Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Review transactions, perform reconciliations, and ensure compliance
          </p>
        </div>

        <AuditDashboard />
      </div>
    </div>
  );
}
