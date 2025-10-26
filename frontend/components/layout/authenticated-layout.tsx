import { AuthenticatedLayoutClient } from "./authenticated-layout-client";
import { createClient } from "@/utils/supabase/server";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";

interface AuthenticatedLayoutProps {
  children: React.ReactNode;
}

export async function AuthenticatedLayout({
  children,
}: AuthenticatedLayoutProps) {
  // Check for wallet authentication first
  const cookieStore = await cookies();
  const walletToken = cookieStore.get("wallet_auth_token")?.value;
  
  if (walletToken) {
    try {
      // Decode JWT payload to check if valid
      const payload = JSON.parse(atob(walletToken.split(".")[1]));
      const exp = payload.exp * 1000;
      
      if (Date.now() < exp) {
        // Create a mock user object for wallet authentication
        const walletUser = {
          email: payload.sub + "@wallet.sui",
          avatar_url: undefined,
          wallet_address: payload.sub,
        };
        
        return (
          <AuthenticatedLayoutClient user={walletUser}>
            {children}
          </AuthenticatedLayoutClient>
        );
      }
    } catch (e) {
      // Invalid wallet token, continue to Supabase check
    }
  }

  // Fall back to Supabase authentication
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
