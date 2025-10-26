import Hero from "./Hero";
import Features from "./Features";
import Architecture from "./Architecture";
import HowItWorks from "./HowItWorks";
import UseCases from "./UseCases";
import CtaSection from "./CTA";
import Footer from "./Footer";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <Hero />
      <Features />
      <Architecture />
      <HowItWorks />
      <UseCases />
      <CtaSection />
      <Footer />
    </div>
  );
}
