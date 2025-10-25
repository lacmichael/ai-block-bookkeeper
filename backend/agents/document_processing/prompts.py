"""
Prompts for document processing and AI-based data extraction.
"""

INVOICE_EXTRACTION_PROMPT = """Extract invoice data from this text and return as JSON:

{text}

Return JSON with the following fields:
- vendor_name: The name of the vendor/supplier
- invoice_number: The invoice number
- invoice_date: The invoice date in YYYY-MM-DD format
- total_amount: The total amount as a number (no currency symbols)
- currency: The currency code (e.g., USD, EUR)
- due_date: The due date in YYYY-MM-DD format
- po_number: The purchase order number (if available)
- payment_terms: The payment terms (e.g., "Net 30", "Due on receipt")

Use null for any missing fields. Return only valid JSON without any markdown formatting."""

