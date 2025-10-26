"use client";

import { useCurrentAccount, useSignPersonalMessage } from "@mysten/dapp-kit";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  clearAuthToken,
  getWalletAddress,
  isWalletAuthenticated,
  requestNonce,
  verifySignature,
} from "@/utils/wallet-auth";

export function useWalletAuth() {
  const currentAccount = useCurrentAccount();
  const { mutateAsync: signPersonalMessage } = useSignPersonalMessage();
  const router = useRouter();
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication status on mount and when account changes
  useEffect(() => {
    const checkAuth = () => {
      const authenticated = isWalletAuthenticated();
      const storedAddress = getWalletAddress();
      
      // If wallet changed, clear auth
      if (authenticated && storedAddress && currentAccount?.address !== storedAddress) {
        clearAuthToken();
        setIsAuthenticated(false);
      } else {
        setIsAuthenticated(authenticated);
      }
    };

    checkAuth();
  }, [currentAccount]);

  const authenticate = useCallback(async () => {
    if (!currentAccount) {
      setError("No wallet connected");
      return false;
    }

    setIsAuthenticating(true);
    setError(null);

    try {
      // Step 1: Request nonce from backend
      const { nonce, message } = await requestNonce(currentAccount.address);

      // Step 2: Sign message with wallet
      const signatureResult = await signPersonalMessage({
        message: new TextEncoder().encode(message),
      });

      // Step 3: Verify signature and get JWT token
      const authData = await verifySignature(
        currentAccount.address,
        signatureResult.signature,
        nonce
      );

      // Step 4: Store the JWT token (Supabase session not needed for wallet auth)
      // The token is already stored by verifySignature function

      setIsAuthenticated(true);
      setIsAuthenticating(false);
      return true;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Authentication failed";
      setError(errorMessage);
      setIsAuthenticating(false);
      return false;
    }
  }, [currentAccount, signPersonalMessage]);

  const signOut = useCallback(async () => {
    clearAuthToken();
    setIsAuthenticated(false);
    router.push("/login");
  }, [router]);

  return {
    currentAccount,
    isAuthenticated,
    isAuthenticating,
    error,
    authenticate,
    signOut,
  };
}

