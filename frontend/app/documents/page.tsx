"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { UploadZone } from "@/components/documents/UploadZone";
import { DocumentsTable } from "@/components/documents/DocumentsTable";
import { Badge } from "@/components/ui/badge";

interface UploadResult {
  document_id: string;
  success: boolean;
  processing_time_seconds: number;
  sui_digest?: string;
  supabase_inserted: boolean;
  document_processing?: {
    success: boolean;
    business_event?: any;
    extracted_data?: any;
    error_message?: string;
  };
  error_message?: string;
}

export default function DocumentsPage() {
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadComplete = (result: UploadResult) => {
    setUploadResult(result);
    // Trigger table refresh
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Documents
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Upload and manage invoice documents
          </p>
        </div>

        {/* Upload Section */}
        <div className="mb-8">
          <UploadZone onUploadComplete={handleUploadComplete} />
        </div>

        {/* Upload Result */}
        {uploadResult && (
          <Card className="mb-8">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Upload Result</CardTitle>
                <Badge variant={uploadResult.success ? "default" : "destructive"}>
                  {uploadResult.success ? "Success" : "Failed"}
                </Badge>
              </div>
              <CardDescription>
                Processing time: {uploadResult.processing_time_seconds.toFixed(2)}s
              </CardDescription>
            </CardHeader>
            <CardContent>
              {uploadResult.success ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                        Document ID
                      </p>
                      <p className="text-sm font-mono mt-1 break-all">
                        {uploadResult.document_id}
                      </p>
                    </div>
                    {uploadResult.sui_digest && (
                      <div>
                        <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                          Sui Digest
                        </p>
                        <p className="text-sm font-mono mt-1 break-all">
                          {uploadResult.sui_digest}
                        </p>
                      </div>
                    )}
                  </div>

                  {uploadResult.document_processing?.business_event && (
                    <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                      <p className="text-sm font-medium mb-2">Extracted Data:</p>
                      <pre className="text-xs overflow-auto max-h-96">
                        {JSON.stringify(
                          uploadResult.document_processing.business_event,
                          null,
                          2
                        )}
                      </pre>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-red-600 dark:text-red-400">
                  <p className="font-medium">Error:</p>
                  <p className="text-sm mt-1">
                    {uploadResult.error_message || "Unknown error occurred"}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Documents Table */}
        <DocumentsTable key={refreshKey} />
      </div>
    </div>
  );
}

