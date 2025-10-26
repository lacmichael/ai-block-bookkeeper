import { type NextRequest, NextResponse } from "next/server";
import { updateSession } from "@/utils/supabase/middleware";

export async function middleware(request: NextRequest) {
  // Check for wallet JWT token in cookies or localStorage (via headers)
  const walletToken = request.cookies.get("wallet_auth_token")?.value || 
                      request.headers.get("authorization")?.replace("Bearer ", "");

  if (walletToken) {
    try {
      // Decode JWT payload (basic check without verification)
      const payload = JSON.parse(atob(walletToken.split(".")[1]));
      const exp = payload.exp * 1000;
      
      // If token is valid, allow access to protected routes
      if (Date.now() < exp) {
        // For protected routes, allow access
        if (request.nextUrl.pathname.startsWith("/dashboard") || 
            request.nextUrl.pathname.startsWith("/transactions") ||
            request.nextUrl.pathname.startsWith("/documents") ||
            request.nextUrl.pathname.startsWith("/audit")) {
          return NextResponse.next();
        }
        // For login page, redirect to dashboard
        if (request.nextUrl.pathname.startsWith("/login")) {
          const url = request.nextUrl.clone();
          url.pathname = "/dashboard";
          return NextResponse.redirect(url);
        }
        return NextResponse.next();
      }
    } catch (e) {
      // Invalid token, continue to Supabase check
    }
  }

  // Fall back to Supabase session check
  return await updateSession(request);
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * Feel free to modify this pattern to include more paths.
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
