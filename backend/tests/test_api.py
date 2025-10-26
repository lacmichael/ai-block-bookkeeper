#!/usr/bin/env python3
"""
Simple test script for the AI Block Bookkeeper API.
Tests the complete pipeline: document upload -> processing -> blockchain posting
"""

import os
import sys
import time
import requests
from pathlib import Path

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")


def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{API_BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Health check passed: {data}")
        return True
    else:
        print(f"✗ Health check failed: {response.status_code}")
        return False


def test_agent_info():
    """Test the agent info endpoint"""
    print("\nTesting agent info...")
    response = requests.get(f"{API_BASE_URL}/agent-info")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Agent info retrieved:")
        print(f"  Document Agent: {data['document_agent_address']} (port {data['document_agent_port']})")
        print(f"  Audit Agent: {data['audit_agent_address']} (port {data['audit_agent_port']})")
        return True
    else:
        print(f"✗ Agent info failed: {response.status_code}")
        return False


def test_process_document(file_path: str):
    """Test document processing endpoint"""
    print(f"\nTesting document processing with: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return False
    
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "application/pdf")}
        data = {"requester_id": "test-user"}
        
        print("Uploading document and waiting for processing...")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/process-document",
                files=files,
                data=data,
                timeout=300  # 5 minute timeout
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Document processed in {elapsed:.2f}s")
                print(f"\nResults:")
                print(f"  Document ID: {result['document_id']}")
                print(f"  Success: {result['success']}")
                print(f"  Processing Time: {result['processing_time_seconds']:.2f}s")
                
                if result.get('document_processing'):
                    doc_proc = result['document_processing']
                    print(f"\n  Document Processing:")
                    print(f"    Success: {doc_proc['success']}")
                    
                    if doc_proc.get('business_event'):
                        event = doc_proc['business_event']
                        print(f"    Event ID: {event.get('event_id')}")
                        print(f"    Amount: ${event.get('amount_minor', 0) / 100:.2f}")
                        print(f"    Event Kind: {event.get('event_kind')}")
                        
                        docs = event.get('documents', [])
                        if docs:
                            confidence = docs[0].get('extraction_confidence', 0.0)
                            print(f"    Confidence: {confidence:.2%}")
                
                if result.get('blockchain_audit'):
                    audit = result['blockchain_audit']
                    print(f"\n  Blockchain Audit:")
                    
                    if audit.get('skipped'):
                        print(f"    Skipped: {audit['reason']}")
                    else:
                        print(f"    Success: {audit.get('success')}")
                        if audit.get('transaction_digest'):
                            print(f"    Digest: {audit['transaction_digest']}")
                        if audit.get('error'):
                            print(f"    Error: {audit['error']}")
                
                if result.get('error_message'):
                    print(f"\n  Error: {result['error_message']}")
                
                return result['success']
            else:
                print(f"✗ Processing failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"✗ Request timed out after {time.time() - start_time:.2f}s")
            return False
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("AI Block Bookkeeper API Test Suite")
    print("=" * 60)
    print(f"API URL: {API_BASE_URL}")
    print("=" * 60)
    
    # Run tests
    results = []
    
    # Test health check
    results.append(("Health Check", test_health_check()))
    
    # Wait a bit for agents to initialize
    time.sleep(1)
    
    # Test agent info
    results.append(("Agent Info", test_agent_info()))
    
    # Test document processing if example file exists
    example_file = Path(__file__).parent / "example" / "example_invoice_01.pdf"
    if example_file.exists():
        results.append(("Document Processing", test_process_document(str(example_file))))
    else:
        print(f"\nSkipping document processing test - example file not found: {example_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

