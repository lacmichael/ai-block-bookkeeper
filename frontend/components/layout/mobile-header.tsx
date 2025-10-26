"use client";

import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";

interface MobileHeaderProps {
  onToggleSidebar: () => void;
  isSidebarOpen: boolean;
}

export function MobileHeader({
  onToggleSidebar,
  isSidebarOpen,
}: MobileHeaderProps) {
  return (
    <div className="md:hidden flex items-center justify-between h-16 px-4 border-b bg-background">
      <h1 className="text-lg font-semibold">booki</h1>
      <Button
        variant="ghost"
        size="sm"
        onClick={onToggleSidebar}
        className="h-8 w-8 p-0"
      >
        {isSidebarOpen ? (
          <X className="h-4 w-4" />
        ) : (
          <Menu className="h-4 w-4" />
        )}
      </Button>
    </div>
  );
}
