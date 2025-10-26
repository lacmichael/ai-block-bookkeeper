"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/utils/utils";
import { cn } from "@/utils/utils";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { navigationItems, type NavigationItem } from "@/utils/navigation";
import { signOut } from "@/app/login/actions";
import { User, ChevronLeft, ChevronRight } from "lucide-react";

interface SidebarProps {
  user: {
    email?: string;
    avatar_url?: string;
  };
}

export function Sidebar({ user }: SidebarProps) {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Load sidebar state from localStorage on mount
  useEffect(() => {
    const savedState = localStorage.getItem("sidebar-collapsed");
    if (savedState !== null) {
      setIsCollapsed(JSON.parse(savedState));
    }
  }, []);

  // Save sidebar state to localStorage when it changes
  useEffect(() => {
    localStorage.setItem("sidebar-collapsed", JSON.stringify(isCollapsed));
  }, [isCollapsed]);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <div
      className={cn(
        "flex h-full flex-col border-r bg-background transition-all duration-300",
        "hidden md:flex", // Hide on mobile by default
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo/Brand */}
      <div className="border-b">
        <div className="flex h-12 items-center justify-center px-4">
          {isCollapsed ? (
            <h2 className="text-lg font-semibold">AB</h2>
          ) : (
            <h2 className="text-lg font-semibold">AI Block Bookkeeper</h2>
          )}
        </div>
        <div className="flex justify-center pb-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebar}
            className="h-8 w-8 p-0"
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-4">
        {navigationItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link key={item.href} href={item.href}>
              <Button
                variant={isActive ? "secondary" : "ghost"}
                className={cn(
                  "w-full h-10 transition-all duration-200",
                  isCollapsed ? "justify-center px-2" : "justify-start gap-3",
                  isActive && "bg-accent text-accent-foreground"
                )}
                title={isCollapsed ? item.title : undefined}
              >
                <Icon className="h-4 w-4" />
                {!isCollapsed && <span className="truncate">{item.title}</span>}
              </Button>
            </Link>
          );
        })}
      </nav>

      {/* User Profile Section */}
      <div className="border-t p-4">
        {isCollapsed ? (
          <div className="flex flex-col items-center space-y-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
              {user.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt="Profile"
                  className="h-8 w-8 rounded-full object-cover"
                />
              ) : (
                <User className="h-4 w-4 text-primary" />
              )}
            </div>
          </div>
        ) : (
          <Card className="p-3">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                {user.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt="Profile"
                    className="h-8 w-8 rounded-full object-cover"
                  />
                ) : (
                  <User className="h-4 w-4 text-primary" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {user.email?.split("@")[0] || "User"}
                </p>
                <p className="text-xs text-muted-foreground truncate">
                  {user.email}
                </p>
              </div>
            </div>
            <form action={signOut} className="w-full">
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                type="submit"
              >
                Sign Out
              </Button>
            </form>
          </Card>
        )}
      </div>
    </div>
  );
}
