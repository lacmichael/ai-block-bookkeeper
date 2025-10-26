"use client";

import { ConnectButton, useCurrentAccount } from "@mysten/dapp-kit";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { useWalletAuth } from "@/hooks/use-wallet-auth";

export function WalletConnectButton() {
  const currentAccount = useCurrentAccount();
  const { authenticate, isAuthenticating, error, isAuthenticated } =
    useWalletAuth();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    // Auto-authenticate when wallet connects and not already authenticated
    if (currentAccount && !isAuthenticated && !isAuthenticating && mounted) {
      authenticate().then((success) => {
        if (success) {
          router.push("/dashboard");
        }
      });
    }
  }, [currentAccount, isAuthenticated, isAuthenticating, authenticate, router, mounted]);

  if (!mounted) {
    return (
      <Button className="w-full" size="lg" disabled>
        Loading...
      </Button>
    );
  }

  return (
    <div className="space-y-2">
      <ConnectButton
        connectText="Connect Sui Wallet"
        className="w-full"
        style={{
          width: "100%",
        }}
      />
      {error && (
        <p className="text-sm text-destructive text-center">{error}</p>
      )}
      {isAuthenticating && (
        <p className="text-sm text-muted-foreground text-center">
          Please sign the message in your wallet...
        </p>
      )}
    </div>
  );
}

