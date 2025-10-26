import { createClient } from "@/utils/supabase/server";
import { redirect } from "next/navigation";
import LandingPage from "@/components/landing/LandingPage";

export default async function Home() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // If user is authenticated, redirect to dashboard
  if (user) {
    redirect("/dashboard");
  }

  // If not authenticated, show landing page
  return <LandingPage />;
}
