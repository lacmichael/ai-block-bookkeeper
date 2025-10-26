import {
  LayoutDashboard,
  FileText,
  Receipt,
  Shield,
} from "lucide-react";

export interface NavigationItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  description?: string;
}

export const navigationItems: NavigationItem[] = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    description: "Overview and analytics",
  },
  {
    title: "Documents",
    href: "/documents",
    icon: FileText,
    description: "Document management",
  },
  {
    title: "Transactions",
    href: "/transactions",
    icon: Receipt,
    description: "View all transactions",
  },
  {
    title: "Reconciliation",
    href: "/reconciliation",
    icon: Shield,
    description: "Audit reconciliation",
  },
];

export const isAuthenticatedRoute = (pathname: string): boolean => {
  const publicRoutes = ["/login", "/auth", "/error"];
  return !publicRoutes.some((route) => pathname.startsWith(route));
};
