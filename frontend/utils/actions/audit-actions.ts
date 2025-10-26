"use server";

import { getBusinessEvents, BusinessEvent } from "./business-events";
import {
  AuditMetadata,
  AuditMetrics,
  ReconciliationCandidate,
  ComplianceRule,
  AuditActivity,
  mockAuditMetadata,
  mockAuditMetrics,
  mockReconciliationCandidates,
  mockComplianceRules,
  mockAuditActivity,
  addAuditMetadataToEvents,
} from "../mockAuditData";

// Simulate API delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function getAuditMetrics(): Promise<AuditMetrics> {
  await delay(800);
  return mockAuditMetrics;
}

export async function getTransactionsForAudit(
  status?: "pending" | "approved" | "rejected" | "flagged",
  limit: number = 50
): Promise<(BusinessEvent & { audit_metadata: AuditMetadata })[]> {
  await delay(600);

  const allEvents = await getBusinessEvents();
  const eventsWithAudit = addAuditMetadataToEvents(allEvents);

  if (status) {
    return eventsWithAudit
      .filter((event) => event.audit_metadata.audit_status === status)
      .slice(0, limit);
  }

  return eventsWithAudit.slice(0, limit);
}

export async function submitAuditDecision(
  eventId: string,
  decision: "approve" | "reject" | "flag",
  notes?: string,
  userId: string = "current.user@company.com"
): Promise<{ success: boolean; message: string }> {
  await delay(1000);

  // Mock the decision submission
  const timestamp = new Date().toISOString();

  // Update mock data (in real app, this would persist to database)
  if (mockAuditMetadata[eventId]) {
    mockAuditMetadata[eventId] = {
      ...mockAuditMetadata[eventId],
      audit_status:
        decision === "approve"
          ? "approved"
          : decision === "reject"
          ? "rejected"
          : "flagged",
      audited_by: userId,
      audited_at: timestamp,
      audit_notes: notes,
    };
  }

  return {
    success: true,
    message: `Transaction ${decision}d successfully`,
  };
}

export async function getReconciliationCandidates(): Promise<{
  invoices: ReconciliationCandidate[];
  bankRecords: ReconciliationCandidate[];
  suggestedMatches: Array<{
    invoice: ReconciliationCandidate;
    bankRecord: ReconciliationCandidate;
    confidence: number;
  }>;
}> {
  await delay(700);

  const invoices = mockReconciliationCandidates.filter(
    (c) => c.type === "invoice"
  );
  const bankRecords = mockReconciliationCandidates.filter(
    (c) => c.type === "bank_record"
  );

  // Generate suggested matches based on amount and date proximity
  const suggestedMatches = [];
  for (const invoice of invoices) {
    for (const bankRecord of bankRecords) {
      const amountMatch = Math.abs(invoice.amount - bankRecord.amount) < 0.01;
      const dateDiff = Math.abs(
        new Date(invoice.date).getTime() - new Date(bankRecord.date).getTime()
      );
      const daysDiff = dateDiff / (1000 * 60 * 60 * 24);

      if (amountMatch && daysDiff <= 7) {
        const confidence = Math.max(0, 100 - daysDiff * 5);
        suggestedMatches.push({
          invoice,
          bankRecord,
          confidence,
        });
      }
    }
  }

  return {
    invoices,
    bankRecords,
    suggestedMatches,
  };
}

export async function submitReconciliation(
  invoiceId: string,
  bankRecordId: string,
  userId: string = "current.user@company.com"
): Promise<{ success: boolean; message: string }> {
  await delay(800);

  // Mock reconciliation submission
  return {
    success: true,
    message: "Reconciliation submitted successfully",
  };
}

export async function getComplianceReport(): Promise<{
  rules: ComplianceRule[];
  overallScore: number;
  violations: ComplianceRule[];
  warnings: ComplianceRule[];
}> {
  await delay(900);

  const violations = mockComplianceRules.filter(
    (rule) => rule.status === "violation"
  );
  const warnings = mockComplianceRules.filter(
    (rule) => rule.status === "warning"
  );
  const compliantRules = mockComplianceRules.filter(
    (rule) => rule.status === "compliant"
  );

  const overallScore = Math.round(
    (compliantRules.length / mockComplianceRules.length) * 100
  );

  return {
    rules: mockComplianceRules,
    overallScore,
    violations,
    warnings,
  };
}

export async function verifyBlockchainRecord(eventId: string): Promise<{
  verified: boolean;
  digest?: string;
  blockHeight?: number;
  confirmations?: number;
  error?: string;
}> {
  await delay(1200);

  // Mock blockchain verification
  const isVerified = Math.random() > 0.1; // 90% success rate

  if (isVerified) {
    return {
      verified: true,
      digest: `0x${Math.random().toString(16).substr(2, 64)}`,
      blockHeight: Math.floor(Math.random() * 1000000) + 50000000,
      confirmations: Math.floor(Math.random() * 100) + 1,
    };
  } else {
    return {
      verified: false,
      error: "Transaction not found on blockchain",
    };
  }
}

export async function getAuditActivity(
  limit: number = 20
): Promise<AuditActivity[]> {
  await delay(500);

  return mockAuditActivity
    .sort(
      (a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    )
    .slice(0, limit);
}

export async function getAnomalyDetection(): Promise<{
  highRiskTransactions: (BusinessEvent & { audit_metadata: AuditMetadata })[];
  flaggedPatterns: Array<{
    pattern: string;
    count: number;
    severity: "low" | "medium" | "high";
  }>;
}> {
  await delay(800);

  const allEvents = await getTransactionsForAudit();
  const highRiskTransactions = allEvents.filter(
    (event) =>
      event.audit_metadata.risk_score && event.audit_metadata.risk_score > 70
  );

  const flaggedPatterns = [
    {
      pattern: "Unusual amounts for vendor",
      count: 3,
      severity: "medium" as const,
    },
    {
      pattern: "Duplicate payment detected",
      count: 1,
      severity: "high" as const,
    },
    {
      pattern: "Missing documentation",
      count: 2,
      severity: "low" as const,
    },
  ];

  return {
    highRiskTransactions,
    flaggedPatterns,
  };
}
