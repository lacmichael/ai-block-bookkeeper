const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface WalletAuthToken {
  access_token: string;
  token_type: string;
  wallet_address: string;
}

/**
 * Store JWT token in localStorage and cookies
 */
export function setAuthToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("wallet_auth_token", token);
    // Also set in cookies for server-side access
    document.cookie = `wallet_auth_token=${token}; path=/; max-age=${24 * 60 * 60}; SameSite=Lax`;
  }
}

/**
 * Get JWT token from localStorage
 */
export function getAuthToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("wallet_auth_token");
  }
  return null;
}

/**
 * Remove JWT token from localStorage and cookies
 */
export function clearAuthToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("wallet_auth_token");
    // Clear cookie by setting it to expire in the past
    document.cookie = "wallet_auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  }
}

/**
 * Check if user is authenticated with wallet
 */
export function isWalletAuthenticated(): boolean {
  const token = getAuthToken();
  if (!token) return false;

  try {
    // Decode JWT payload (without verification, just to check expiry)
    const payload = JSON.parse(atob(token.split(".")[1]));
    const exp = payload.exp * 1000; // Convert to milliseconds
    return Date.now() < exp;
  } catch {
    return false;
  }
}

/**
 * Get wallet address from stored token
 */
export function getWalletAddress(): string | null {
  const token = getAuthToken();
  if (!token) return null;

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    // For custom JWT tokens, wallet address is in 'sub' field
    // For Supabase tokens, it would be in user_metadata.wallet_address
    return payload.sub || payload.user_metadata?.wallet_address || null;
  } catch {
    return null;
  }
}

/**
 * Request nonce from backend for authentication
 */
export async function requestNonce(
  walletAddress: string
): Promise<{ nonce: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/auth/wallet/nonce`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ wallet_address: walletAddress }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to request nonce" }));
    throw new Error(error.detail || "Failed to request nonce");
  }

  return response.json();
}

/**
 * Verify signature and get JWT token
 */
export async function verifySignature(
  walletAddress: string,
  signature: string,
  nonce: string
): Promise<WalletAuthToken> {
  const response = await fetch(`${API_BASE_URL}/auth/wallet/verify`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      wallet_address: walletAddress,
      signature,
      nonce,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Signature verification failed" }));
    throw new Error(error.detail || "Signature verification failed");
  }

  const data = await response.json();
  setAuthToken(data.access_token);
  return data;
}

/**
 * Refresh JWT token
 */
export async function refreshToken(): Promise<WalletAuthToken> {
  const token = getAuthToken();
  if (!token) {
    throw new Error("No token to refresh");
  }

  const response = await fetch(`${API_BASE_URL}/auth/wallet/refresh`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    clearAuthToken();
    throw new Error("Token refresh failed");
  }

  const data = await response.json();
  setAuthToken(data.access_token);
  return data;
}

/**
 * Create authenticated API client
 */
export function createAuthenticatedClient() {
  const token = getAuthToken();

  return {
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  };
}

