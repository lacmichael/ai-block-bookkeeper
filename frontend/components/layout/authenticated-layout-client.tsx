"use client";

import { useState } from "react";
import { Sidebar } from "./sidebar";
import { MobileHeader } from "./mobile-header";

interface AuthenticatedLayoutClientProps {
  children: React.ReactNode;
  user: {
    email?: string;
    avatar_url?: string;
    wallet_address?: string;
  };
}

export function AuthenticatedLayoutClient({
  children,
  user,
}: AuthenticatedLayoutClientProps) {
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  const toggleMobileSidebar = () => {
    setIsMobileSidebarOpen(!isMobileSidebarOpen);
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Mobile Header */}
      <MobileHeader
        onToggleSidebar={toggleMobileSidebar}
        isSidebarOpen={isMobileSidebarOpen}
      />

      {/* Desktop Sidebar */}
      <Sidebar user={user} />

      {/* Mobile Sidebar Overlay */}
      {isMobileSidebarOpen && (
        <div className="md:hidden fixed inset-0 z-50">
          <div
            className="fixed inset-0 bg-black/50"
            onClick={() => setIsMobileSidebarOpen(false)}
          />
          <div className="fixed left-0 top-0 h-full w-64 bg-background border-r">
            <Sidebar user={user} />
          </div>
        </div>
      )}

      <main className="flex-1 overflow-auto transition-all duration-300">
        {children}
      </main>
    </div>
  );
}
