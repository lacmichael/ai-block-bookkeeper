import { AuthenticatedLayoutClient } from "./authenticated-layout-client";
import { createClient } from "@/utils/supabase/server";
import { redirect } from "next/navigation";

interface AuthenticatedLayoutProps {
  children: React.ReactNode;
}

export async function AuthenticatedLayout({
  children,
}: AuthenticatedLayoutProps) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // If user is not authenticated, redirect to login
  if (!user) {
    redirect("/login");
  }

  return (
    <AuthenticatedLayoutClient user={user}>
      {children}
    </AuthenticatedLayoutClient>
  );
}
