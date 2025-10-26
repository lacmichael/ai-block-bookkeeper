"use client";

import { useState } from "react";
import { ArrowRight, Calendar, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function CtaSection() {
  const [email, setEmail] = useState("");
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Here you would typically send the email to your backend
    console.log("Email submitted:", email);
    setIsSubmitted(true);
    setEmail(""); // Clear the input
  };

  return (
    <section className="relative py-24 section-dark overflow-hidden">
      <div className="absolute inset-0 gradient-hero opacity-50"></div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="glass rounded-3xl p-8 md:p-12 text-center">
          {/* Main Content */}
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight mb-6">
            <span className="text-foreground">Ready to Transform Your</span>
            <br />
            <span className="text-foreground">Financial Infrastructure?</span>
          </h2>

          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join the future of accounting with AscendTech. Get early access to
            our revolutionary blockchain-powered platform.
          </p>

          {/* Email Capture Form */}
          {isSubmitted ? (
            <div className="max-w-md mx-auto mb-8">
              <div className="flex items-center justify-center gap-2 text-green-600 mb-4">
                <CheckCircle className="w-6 h-6" />
                <span className="font-semibold">
                  Thank you for your interest!
                </span>
              </div>
              <p className="text-muted-foreground">
                We'll be in touch soon with early access details.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="max-w-md mx-auto mb-8">
              <div className="flex flex-col sm:flex-row gap-4">
                <Input
                  type="email"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="flex-1 glass border-border/50"
                  required
                />
                <Button
                  type="submit"
                  size="lg"
                  className="gradient-primary hover-glow-primary whitespace-nowrap"
                >
                  Get Access
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </div>
            </form>
          )}

          {/* MVP Launch Indicator */}
          <div className="flex items-center justify-center gap-2 text-muted-foreground mb-8">
            <Calendar className="w-5 h-5" />
            <span className="text-sm">MVP Launch: Q2 2024</span>
          </div>

          {/* Additional CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              asChild
              variant="outline"
              size="lg"
              className="glass hover-glow-accent"
            >
              <a href="/login">Start Free Trial</a>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="glass hover-glow-accent"
            >
              <a href="#architecture">View Technical Details</a>
            </Button>
          </div>

          {/* Trust Indicators */}
          <div className="mt-12 pt-8 border-t border-border/50">
            <div className="flex flex-wrap justify-center gap-8 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                <span>Secure & Compliant</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                <span>Cloud-Native</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                <span>Real-time Processing</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
