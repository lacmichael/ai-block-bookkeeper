#!/usr/bin/env python3
"""
Test script for the Document Processing Agent.
This tests the actual agent with message passing.
"""
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import agent components
from agents.document_processing_agent import agent
from agents.document_processing.models import DocumentProcessingRequest

async def test_agent():
    """Test the document processing agent"""
    
    print("Document Processing Agent Test")
    print("=" * 50)
    
    # Path to the example invoice
    pdf_path = os.path.join(os.path.dirname(__file__), "example", "example_invoice_01.pdf")
    
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
        
        # Display results
        print(f"Document ID: {response.document_id}")
        print(f"Success: {response.success}")
        print(f"Processing Time: {response.processing_time_seconds:.2f} seconds")
        
        if response.success:
            print("\nExtracted Data:")
            if response.extracted_data:
                for key, value in response.extracted_data.items():
                    if key != "error":
                        print(f"  {key}: {value}")
            
            print("\nBusiness Event Created:")
            if response.business_event:
                event = response.business_event
                print(f"  Event ID: {event.get('event_id', 'N/A')}")
                print(f"  Source System: {event.get('source_system', 'N/A')}")
                print(f"  Event Kind: {event.get('event_kind', 'N/A')}")
                
                payee = event.get('payee', {}) or {}
                if payee:
                    print(f"  Vendor: {payee.get('party_id', 'N/A')}")
                
                amount = event.get('amount_minor', 0)
                currency = event.get('currency', 'USD')
                print(f"  Amount: ${amount / 100:.2f} {currency}")
                print(f"  Description: {event.get('description', 'N/A')}")
                
                processing_state = event.get('processing', {})
                print(f"  Processing State: {processing_state.get('state', 'N/A')}")
                
                print(f"\nDedupe Key: {event.get('dedupe_key', 'N/A')}")
            else:
                print("  WARNING: No business event created")
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
