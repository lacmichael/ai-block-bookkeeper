"""
Prompts for document processing and AI-based data extraction.
"""

INVOICE_EXTRACTION_PROMPT = """Extract invoice data from this text and return as JSON:

{text}

Return JSON with the following fields:

REQUIRED FIELDS:
- vendor_name: The name of the vendor/supplier
- invoice_number: The invoice number
- invoice_date: The invoice date in YYYY-MM-DD format
- total_amount: The total amount as a number (no currency symbols)
- currency: The currency code (e.g., USD, EUR)

OPTIONAL FIELDS (extract if available):
- due_date: The due date in YYYY-MM-DD format
- po_number: The purchase order number
- payment_terms: The payment terms (e.g., "Net 30", "Due on receipt")
- description: General description or memo about the invoice/transaction

VENDOR/PAYEE DETAILS (extract if available):
- vendor_legal_name: Full legal name of the vendor if different from vendor_name
- vendor_email: Vendor contact email
- vendor_address: Vendor address as a structured object with fields: street, city, state, postal_code, country
- vendor_tax_id: Vendor tax ID or EIN (if present)

PAYER/CUSTOMER DETAILS (extract if available):
- payer_name: Name of the customer/buyer (the entity receiving the invoice)
- payer_legal_name: Full legal name of the payer
- payer_email: Payer contact email
- payer_address: Payer address as a structured object with fields: street, city, state, postal_code, country
- payer_tax_id: Payer tax ID (if present)

LINE ITEMS (extract if available):
- line_items: Array of line items, each containing:
  - description: Item description
  - quantity: Quantity
  - unit_price: Price per unit
  - amount: Total line amount
  - category: Item category if specified
  - tax_amount: Tax for this line item if specified

FINANCIAL DETAILS (extract if available):
- subtotal: Subtotal before taxes
- tax_amount: Total tax amount
- tax_rate: Tax rate percentage
- tax_jurisdiction: Tax jurisdiction (e.g., state, country)
- discount_amount: Any discount applied
- shipping_amount: Shipping/delivery charges

METADATA (extract any other relevant information):
- notes: Any additional notes or comments on the invoice
- reference_numbers: Any other reference numbers (order numbers, job numbers, etc.)

Use null for any missing fields. Return only valid JSON without any markdown formatting."""

