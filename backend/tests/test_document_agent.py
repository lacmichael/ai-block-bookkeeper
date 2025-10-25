#!/usr/bin/env python3
"""
Test script for the Document Processing Agent.
This tests the actual agent with message passing.
"""
import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Import agent components
from agents.document_processing_agent import agent
from agents.document_processing.models import DocumentProcessingRequest

async def test_agent():
    """Test the document processing agent"""
    
    print("Document Processing Agent Test")
    print("=" * 50)
    
    # Path to the example invoice (go up one directory from tests/)
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "example", "example_invoice_01.pdf")
    pdf_path = os.path.abspath(pdf_path)  # Resolve to absolute path
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return
    
    print(f"Testing with: {pdf_path}")
    print(f"Agent Address: {agent.address}")
    print("=" * 50)
    
    # Create a document processing request
    request = DocumentProcessingRequest(
        document_id="test_doc_001",
        file_path=pdf_path,
        filename="example_invoice_01.pdf",
        file_size=os.path.getsize(pdf_path),
        file_type="PDF",
        upload_timestamp=datetime.utcnow(),
        requester_id="test_user"
    )
    
    print("Sending request to agent...")
    print(f"   Document ID: {request.document_id}")
    print(f"   File: {request.filename}")
    
    try:
        # This is a simple test that calls the agent's handler directly
        # In production, you would send messages between agents
        from agents.document_processing_agent import processing_client
        
        print("\nProcessing document through client...")
        
        # Process through the client (same as agent does)
        response = await processing_client.process_document(request)
        
        print("\nAgent processing completed!")
        print("=" * 50)
        
        # Display results summary
        print(f"\nDocument ID: {response.document_id}")
        print(f"Success: {response.success}")
        print(f"Processing Time: {response.processing_time_seconds:.2f} seconds")
        
        if response.success:
            # Display extracted data as JSON
            print("\n" + "=" * 50)
            print("EXTRACTED DATA (Raw AI Output)")
            print("=" * 50)
            if response.extracted_data:
                print(json.dumps(response.extracted_data, indent=2, default=str))
            else:
                print("No extracted data available")
            
            # Display business event as JSON
            print("\n" + "=" * 50)
            print("BUSINESS EVENT (Structured Domain Model)")
            print("=" * 50)
            if response.business_event:
                # Quick summary before full JSON
                event = response.business_event
                amount = event.get('amount_minor', 0)
                currency = event.get('currency', 'USD')
                vendor = event.get('payee', {})
                payer = event.get('payer', {})
                
                print(f"\n Quick Summary:")
                print(f"  Event ID: {event.get('event_id', 'N/A')}")
                print(f"  Vendor: {vendor.get('party_id', 'N/A') if vendor else 'N/A'}")
                print(f"  Payer: {payer.get('party_id', 'N/A') if payer else 'N/A'}")
                print(f"  Amount: {currency} ${amount / 100:.2f}")
                print(f"  Processing State: {event.get('processing', {}).get('state', 'N/A')}")
                
                # Print full business event
                print(f"\n Full Business Event JSON:")
                print(json.dumps(event, indent=2, default=str))
                
                # Highlight metadata sections if present
                metadata = event.get('metadata', {})
                if metadata:
                    print(f"\n  Metadata Sections Present:")
                    for key in metadata.keys():
                        if key != 'raw_extraction':
                            value = metadata[key]
                            if isinstance(value, dict):
                                print(f"    - {key}: {len(value)} fields")
                            elif isinstance(value, list):
                                print(f"    - {key}: {len(value)} items")
                            else:
                                print(f"    - {key}")
            else:
                print("WARNING: No business event created")
        else:
            print(f"\nError: {response.error_message}")
        
        print("\n" + "=" * 50)
        print("Agent test completed successfully!")
        
    except Exception as e:
        print(f"\nAgent test failed with error: {str(e)}")
        import traceback
        print("\nTraceback:")
        traceback.print_exc()
        print("\nMake sure to:")
        print("  1. Set ANTHROPIC_API_KEY in your .env file")
        print("  2. Install all dependencies from requirements.txt")

if __name__ == "__main__":
    asyncio.run(test_agent())
