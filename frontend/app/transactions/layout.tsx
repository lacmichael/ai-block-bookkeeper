import { AuthenticatedLayout } from "@/components/layout/authenticated-layout";

export default function TransactionsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthenticatedLayout>{children}</AuthenticatedLayout>;
}
