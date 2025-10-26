import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";

interface AuthCodeErrorPageProps {
  searchParams: {
    error?: string;
    description?: string;
  };
}

export default function AuthCodeErrorPage({
  searchParams,
}: AuthCodeErrorPageProps) {
  const { error, description } = searchParams;
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-red-600">
            Authentication Error
          </CardTitle>
          <CardDescription>
            There was an error processing your authentication request.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-md">
              <p className="text-sm font-medium text-red-800 dark:text-red-200">
                Error: {error}
              </p>
              {description && (
                <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                  {description}
                </p>
              )}
            </div>
          )}
          <p className="text-sm text-gray-600 dark:text-gray-400">
            This could be due to:
          </p>
          <ul className="text-sm text-gray-600 dark:text-gray-400 list-disc list-inside space-y-1">
            <li>Invalid or expired authentication code</li>
            <li>Network connectivity issues</li>
            <li>OAuth provider configuration problems</li>
            <li>Incorrect redirect URL configuration</li>
          </ul>
          <div className="pt-4">
            <Link href="/login">
              <Button className="w-full">Try Again</Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
