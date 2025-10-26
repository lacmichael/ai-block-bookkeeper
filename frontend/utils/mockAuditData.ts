import { BusinessEvent } from "./actions/business-events";

export interface AuditMetadata {
  audit_status: "pending" | "approved" | "rejected" | "flagged";
  audited_by?: string;
  audited_at?: string;
  audit_notes?: string;
  anomaly_flags?: string[];
  compliance_status?: "compliant" | "non_compliant" | "requires_review";
  risk_score?: number; // 0-100
  verification_status?: "unverified" | "verified" | "failed";
}

export interface AuditMetrics {
  pending_audits: number;
  approved_count: number;
  rejected_count: number;
  flagged_count: number;
  reconciliation_rate: number;
  compliance_score: number;
  anomaly_alerts: number;
  high_risk_transactions: number;
}

export interface ReconciliationCandidate {
  id: string;
  type: "invoice" | "bank_record";
  amount: number;
  date: string;
  description: string;
  party_name: string;
  source: string;
  matched_with?: string;
  confidence_score?: number;
}

export interface ComplianceRule {
  id: string;
  name: string;
  description: string;
  severity: "low" | "medium" | "high" | "critical";
  status: "compliant" | "violation" | "warning";
  affected_transactions: number;
  last_checked: string;
}

export interface AuditActivity {
  id: string;
  timestamp: string;
  action: string;
  transaction_id: string;
  user: string;
  details: string;
}

// Mock audit metadata for business events
export const mockAuditMetadata: Record<string, AuditMetadata> = {
  evt_001: {
    audit_status: "approved",
    audited_by: "john.doe@company.com",
    audited_at: "2024-01-15T10:30:00Z",
    audit_notes: "All documentation verified. Amount matches invoice.",
    compliance_status: "compliant",
    risk_score: 15,
    verification_status: "verified",
  },
  evt_002: {
    audit_status: "flagged",
    audited_by: "jane.smith@company.com",
    audited_at: "2024-01-15T14:20:00Z",
    audit_notes:
      "Unusual amount for this vendor. Requires additional verification.",
    anomaly_flags: ["unusual_amount", "vendor_mismatch"],
    compliance_status: "requires_review",
    risk_score: 75,
    verification_status: "unverified",
  },
  evt_003: {
    audit_status: "pending",
    compliance_status: "compliant",
    risk_score: 25,
    verification_status: "unverified",
  },
  evt_004: {
    audit_status: "rejected",
    audited_by: "mike.wilson@company.com",
    audited_at: "2024-01-14T16:45:00Z",
    audit_notes: "Missing supporting documentation. Invoice not found.",
    compliance_status: "non_compliant",
    risk_score: 90,
    verification_status: "failed",
  },
  evt_005: {
    audit_status: "approved",
    audited_by: "sarah.jones@company.com",
    audited_at: "2024-01-15T09:15:00Z",
    audit_notes: "Standard transaction. All checks passed.",
    compliance_status: "compliant",
    risk_score: 10,
    verification_status: "verified",
  },
};

// Mock audit metrics
export const mockAuditMetrics: AuditMetrics = {
  pending_audits: 12,
  approved_count: 45,
  rejected_count: 3,
  flagged_count: 8,
  reconciliation_rate: 87.5,
  compliance_score: 92.3,
  anomaly_alerts: 5,
  high_risk_transactions: 2,
};

// Mock reconciliation candidates
export const mockReconciliationCandidates: ReconciliationCandidate[] = [
  {
    id: "inv_001",
    type: "invoice",
    amount: 2500.0,
    date: "2024-01-15",
    description: "Office supplies invoice",
    party_name: "Office Depot",
    source: "INVOICE_RECEIVED",
    confidence_score: 95,
  },
  {
    id: "bank_001",
    type: "bank_record",
    amount: 2500.0,
    date: "2024-01-16",
    description: "ACH Payment - Office Depot",
    party_name: "Office Depot",
    source: "BANK_POSTED",
    confidence_score: 95,
  },
  {
    id: "inv_002",
    type: "invoice",
    amount: 15000.0,
    date: "2024-01-14",
    description: "Software licensing fee",
    party_name: "Microsoft Corp",
    source: "INVOICE_RECEIVED",
    confidence_score: 88,
  },
  {
    id: "bank_002",
    type: "bank_record",
    amount: 15000.0,
    date: "2024-01-15",
    description: "Wire Transfer - Microsoft",
    party_name: "Microsoft Corp",
    source: "BANK_POSTED",
    confidence_score: 88,
  },
  {
    id: "inv_003",
    type: "invoice",
    amount: 500.0,
    date: "2024-01-13",
    description: "Consulting services",
    party_name: "TechConsult Inc",
    source: "INVOICE_RECEIVED",
  },
  {
    id: "bank_003",
    type: "bank_record",
    amount: 500.0,
    date: "2024-01-14",
    description: "Check payment - TechConsult",
    party_name: "TechConsult Inc",
    source: "BANK_POSTED",
  },
];

// Mock compliance rules
export const mockComplianceRules: ComplianceRule[] = [
  {
    id: "rule_001",
    name: "High Value Approval",
    description: "All transactions over $10,000 require manager approval",
    severity: "high",
    status: "compliant",
    affected_transactions: 3,
    last_checked: "2024-01-15T10:00:00Z",
  },
  {
    id: "rule_002",
    name: "Documentation Required",
    description: "All invoices must have supporting documentation",
    severity: "medium",
    status: "violation",
    affected_transactions: 2,
    last_checked: "2024-01-15T10:00:00Z",
  },
  {
    id: "rule_003",
    name: "Duplicate Detection",
    description: "No duplicate payments allowed within 7 days",
    severity: "critical",
    status: "compliant",
    affected_transactions: 0,
    last_checked: "2024-01-15T10:00:00Z",
  },
  {
    id: "rule_004",
    name: "Vendor Verification",
    description: "All new vendors must be verified before payment",
    severity: "medium",
    status: "warning",
    affected_transactions: 1,
    last_checked: "2024-01-15T10:00:00Z",
  },
];

// Mock audit activity
export const mockAuditActivity: AuditActivity[] = [
  {
    id: "activity_001",
    timestamp: "2024-01-15T14:30:00Z",
    action: "approved",
    transaction_id: "evt_001",
    user: "john.doe@company.com",
    details: "Transaction approved after document verification",
  },
  {
    id: "activity_002",
    timestamp: "2024-01-15T14:20:00Z",
    action: "flagged",
    transaction_id: "evt_002",
    user: "jane.smith@company.com",
    details: "Flagged for unusual amount - requires additional review",
  },
  {
    id: "activity_003",
    timestamp: "2024-01-15T13:45:00Z",
    action: "rejected",
    transaction_id: "evt_004",
    user: "mike.wilson@company.com",
    details: "Rejected due to missing supporting documentation",
  },
  {
    id: "activity_004",
    timestamp: "2024-01-15T12:15:00Z",
    action: "reconciled",
    transaction_id: "evt_005",
    user: "sarah.jones@company.com",
    details: "Successfully reconciled with bank record",
  },
  {
    id: "activity_005",
    timestamp: "2024-01-15T11:30:00Z",
    action: "compliance_check",
    transaction_id: "evt_003",
    user: "system",
    details: "Automated compliance check passed",
  },
];

// Helper function to get audit metadata for a transaction
export function getAuditMetadata(eventId: string): AuditMetadata {
  return (
    mockAuditMetadata[eventId] || {
      audit_status: "pending",
      compliance_status: "compliant",
      risk_score: 50,
      verification_status: "unverified",
    }
  );
}

// Helper function to add audit metadata to business events
export function addAuditMetadataToEvents(
  events: BusinessEvent[]
): (BusinessEvent & { audit_metadata: AuditMetadata })[] {
  return events.map((event) => ({
    ...event,
    audit_metadata: getAuditMetadata(event.event_id),
  }));
}
