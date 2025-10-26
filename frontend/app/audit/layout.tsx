import { AuthenticatedLayout } from "@/components/layout/authenticated-layout";

export default function AuditLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthenticatedLayout>{children}</AuthenticatedLayout>;
}
