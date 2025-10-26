import { AuthenticatedLayout } from "@/components/layout/authenticated-layout";

export default function DocumentsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthenticatedLayout>{children}</AuthenticatedLayout>;
}

