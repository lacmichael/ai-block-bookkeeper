// Mock financial data for the dashboard
export interface BusinessEvent {
  event_id: string;
  source_system: "PLAID" | "MANUAL" | "INVOICE_PORTAL" | "SUI" | "OTHER";
  source_id: string;
  occurred_at: string;
  recorded_at: string;
  event_kind:
    | "BANK_POSTED"
    | "INVOICE_RECEIVED"
    | "PAYMENT_SENT"
    | "REFUND"
    | "ADJUSTMENT";
  amount_minor: number;
  currency: string;
  description: string;
  payer?: {
    party_id: string;
    role: "VENDOR" | "CUSTOMER" | "EMPLOYEE" | "INTERNAL";
  };
  payee?: {
    party_id: string;
    role: "VENDOR" | "CUSTOMER" | "EMPLOYEE" | "INTERNAL";
  };
  processing: {
    state: "PENDING" | "MAPPED" | "POSTED_ONCHAIN" | "INDEXED" | "FAILED";
    last_error?: string;
  };
  reconciliation_state: "UNRECONCILED" | "PARTIAL" | "RECONCILED";
}

export interface FinancialMetrics {
  totalRevenue: number;
  totalExpenses: number;
  netProfit: number;
  reconciliationRate: number;
  revenueChange: number;
  expenseChange: number;
  profitChange: number;
  reconciliationChange: number;
}

export interface ChartData {
  month: string;
  revenue: number;
  expenses: number;
  cashFlow: number;
}

export interface TransactionTypeData {
  type: string;
  value: number;
  count: number;
}

export interface ReconciliationData {
  status: string;
  value: number;
  count: number;
}

// Mock business events (transactions)
export const mockBusinessEvents: BusinessEvent[] = [
  {
    event_id: "evt_001",
    source_system: "INVOICE_PORTAL",
    source_id: "inv_2024_001",
    occurred_at: "2024-01-15T10:30:00Z",
    recorded_at: "2024-01-15T10:35:00Z",
    event_kind: "INVOICE_RECEIVED",
    amount_minor: 250000, // $2,500.00
    currency: "USD",
    description: "Website Development Services - Q1 2024",
    payer: {
      party_id: "party_customer_001",
      role: "CUSTOMER",
    },
    payee: {
      party_id: "party_vendor_001",
      role: "VENDOR",
    },
    processing: {
      state: "POSTED_ONCHAIN",
    },
    reconciliation_state: "RECONCILED",
  },
  {
    event_id: "evt_002",
    source_system: "PLAID",
    source_id: "bank_txn_001",
    occurred_at: "2024-01-14T14:20:00Z",
    recorded_at: "2024-01-14T14:25:00Z",
    event_kind: "BANK_POSTED",
    amount_minor: -150000, // -$1,500.00
    currency: "USD",
    description: "Office Rent Payment - January 2024",
    payer: {
      party_id: "party_internal_001",
      role: "INTERNAL",
    },
    payee: {
      party_id: "party_vendor_002",
      role: "VENDOR",
    },
    processing: {
      state: "INDEXED",
    },
    reconciliation_state: "RECONCILED",
  },
  {
    event_id: "evt_003",
    source_system: "MANUAL",
    source_id: "manual_001",
    occurred_at: "2024-01-13T09:15:00Z",
    recorded_at: "2024-01-13T09:20:00Z",
    event_kind: "PAYMENT_SENT",
    amount_minor: -75000, // -$750.00
    currency: "USD",
    description: "Software License Renewal - Adobe Creative Suite",
    payer: {
      party_id: "party_internal_001",
      role: "INTERNAL",
    },
    payee: {
      party_id: "party_vendor_003",
      role: "VENDOR",
    },
    processing: {
      state: "MAPPED",
    },
    reconciliation_state: "UNRECONCILED",
  },
  {
    event_id: "evt_004",
    source_system: "INVOICE_PORTAL",
    source_id: "inv_2024_002",
    occurred_at: "2024-01-12T16:45:00Z",
    recorded_at: "2024-01-12T16:50:00Z",
    event_kind: "INVOICE_RECEIVED",
    amount_minor: 180000, // $1,800.00
    currency: "USD",
    description: "Marketing Campaign - Social Media Management",
    payer: {
      party_id: "party_customer_002",
      role: "CUSTOMER",
    },
    payee: {
      party_id: "party_vendor_001",
      role: "VENDOR",
    },
    processing: {
      state: "POSTED_ONCHAIN",
    },
    reconciliation_state: "RECONCILED",
  },
  {
    event_id: "evt_005",
    source_system: "PLAID",
    source_id: "bank_txn_002",
    occurred_at: "2024-01-11T11:30:00Z",
    recorded_at: "2024-01-11T11:35:00Z",
    event_kind: "BANK_POSTED",
    amount_minor: -45000, // -$450.00
    currency: "USD",
    description: "Utilities Payment - Electricity & Internet",
    payer: {
      party_id: "party_internal_001",
      role: "INTERNAL",
    },
    payee: {
      party_id: "party_vendor_004",
      role: "VENDOR",
    },
    processing: {
      state: "INDEXED",
    },
    reconciliation_state: "PARTIAL",
  },
  {
    event_id: "evt_006",
    source_system: "MANUAL",
    source_id: "manual_002",
    occurred_at: "2024-01-10T13:20:00Z",
    recorded_at: "2024-01-10T13:25:00Z",
    event_kind: "REFUND",
    amount_minor: 25000, // $250.00
    currency: "USD",
    description: "Customer Refund - Overpayment Correction",
    payer: {
      party_id: "party_internal_001",
      role: "INTERNAL",
    },
    payee: {
      party_id: "party_customer_003",
      role: "CUSTOMER",
    },
    processing: {
      state: "PENDING",
    },
    reconciliation_state: "UNRECONCILED",
  },
  {
    event_id: "evt_007",
    source_system: "INVOICE_PORTAL",
    source_id: "inv_2024_003",
    occurred_at: "2024-01-09T08:45:00Z",
    recorded_at: "2024-01-09T08:50:00Z",
    event_kind: "INVOICE_RECEIVED",
    amount_minor: 320000, // $3,200.00
    currency: "USD",
    description: "E-commerce Platform Development",
    payer: {
      party_id: "party_customer_004",
      role: "CUSTOMER",
    },
    payee: {
      party_id: "party_vendor_001",
      role: "VENDOR",
    },
    processing: {
      state: "POSTED_ONCHAIN",
    },
    reconciliation_state: "RECONCILED",
  },
  {
    event_id: "evt_008",
    source_system: "PLAID",
    source_id: "bank_txn_003",
    occurred_at: "2024-01-08T15:10:00Z",
    recorded_at: "2024-01-08T15:15:00Z",
    event_kind: "BANK_POSTED",
    amount_minor: -95000, // -$950.00
    currency: "USD",
    description: "Employee Salary - John Smith",
    payer: {
      party_id: "party_internal_001",
      role: "INTERNAL",
    },
    payee: {
      party_id: "party_employee_001",
      role: "EMPLOYEE",
    },
    processing: {
      state: "INDEXED",
    },
    reconciliation_state: "RECONCILED",
  },
  {
    event_id: "evt_009",
    source_system: "MANUAL",
    source_id: "manual_003",
    occurred_at: "2024-01-07T12:00:00Z",
    recorded_at: "2024-01-07T12:05:00Z",
    event_kind: "ADJUSTMENT",
    amount_minor: -5000, // -$50.00
    currency: "USD",
    description: "Bank Fee Adjustment - Wire Transfer",
    payer: {
      party_id: "party_internal_001",
      role: "INTERNAL",
    },
    processing: {
      state: "MAPPED",
    },
    reconciliation_state: "RECONCILED",
  },
  {
    event_id: "evt_010",
    source_system: "INVOICE_PORTAL",
    source_id: "inv_2024_004",
    occurred_at: "2024-01-06T14:30:00Z",
    recorded_at: "2024-01-06T14:35:00Z",
    event_kind: "INVOICE_RECEIVED",
    amount_minor: 120000, // $1,200.00
    currency: "USD",
    description: "SEO Optimization Services",
    payer: {
      party_id: "party_customer_005",
      role: "CUSTOMER",
    },
    payee: {
      party_id: "party_vendor_001",
      role: "VENDOR",
    },
    processing: {
      state: "POSTED_ONCHAIN",
    },
    reconciliation_state: "RECONCILED",
  },
];

// Mock financial metrics
export const mockFinancialMetrics: FinancialMetrics = {
  totalRevenue: 870000, // $8,700.00
  totalExpenses: 370000, // $3,700.00
  netProfit: 500000, // $5,000.00
  reconciliationRate: 75, // 75%
  revenueChange: 12.5, // +12.5%
  expenseChange: -3.2, // -3.2%
  profitChange: 18.7, // +18.7%
  reconciliationChange: 5.2, // +5.2%
};

// Mock chart data for monthly trends
export const mockChartData: ChartData[] = [
  { month: "Oct", revenue: 650000, expenses: 420000, cashFlow: 230000 },
  { month: "Nov", revenue: 720000, expenses: 380000, cashFlow: 340000 },
  { month: "Dec", revenue: 810000, expenses: 450000, cashFlow: 360000 },
  { month: "Jan", revenue: 870000, expenses: 370000, cashFlow: 500000 },
];

// Mock transaction type distribution
export const mockTransactionTypeData: TransactionTypeData[] = [
  { type: "Invoice Received", value: 750000, count: 4 },
  { type: "Bank Posted", value: 290000, count: 3 },
  { type: "Payment Sent", value: 75000, count: 1 },
  { type: "Refund", value: 25000, count: 1 },
  { type: "Adjustment", value: 5000, count: 1 },
];

// Mock reconciliation status data
export const mockReconciliationData: ReconciliationData[] = [
  { status: "Reconciled", value: 650000, count: 6 },
  { status: "Unreconciled", value: 150000, count: 2 },
  { status: "Partial", value: 45000, count: 1 },
];

// Helper function to format currency
export const formatCurrency = (amountMinor: number): string => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amountMinor / 100);
};

// Helper function to format percentage
export const formatPercentage = (value: number): string => {
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}%`;
};
