import { ComplianceChecklist } from "@/components/audit/ComplianceChecklist";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function CompliancePage() {
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

        <ComplianceChecklist />
      </div>
    </div>
  );
}
