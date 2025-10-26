"use client";

import Link from "next/link";
import { Zap, Shield, Brain, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-background">
      {/* Enhanced Animated Background Orbs */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary/30 rounded-full blur-3xl animate-pulse-glow"></div>
        <div
          className="absolute -bottom-40 -left-40 w-96 h-96 bg-accent/30 rounded-full blur-3xl animate-pulse-glow"
          style={{ animationDelay: "1.5s" }}
        ></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/10 rounded-full blur-3xl animate-pulse-gradient"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Enhanced Top Badge */}
        <div className="mb-8">
          <Badge
            variant="outline"
            className="glass px-6 py-3 text-sm font-medium border-primary/40"
          >
            <Zap className="w-4 h-4 mr-2 text-primary" />
            Powered by Fetch.ai Autonomous Agents & Sui Blockchain
          </Badge>
        </div>

        {/* Enhanced Main Heading */}
        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-6">
          <span className="text-foreground">Autonomous Blockchain</span>
          <br />
          <span className="text-foreground">Accounting Service</span>
        </h1>

        {/* Enhanced Subheading */}
        <p className="text-xl sm:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed">
          Replace centralized, mutable accounting records with an immutable,
          cryptographically verifiable ledger for superior auditability and
          end-to-end autonomous financial analysis.
        </p>

        {/* Enhanced Feature Pills */}
        <div className="flex flex-wrap justify-center gap-4 mb-12">
          <div className="flex items-center gap-2 glass px-4 py-2 rounded-full border-primary/20">
            <Shield className="w-5 h-5 text-primary" />
            <span className="text-sm font-medium">Immutable Records</span>
          </div>
          <div className="flex items-center gap-2 glass px-4 py-2 rounded-full border-primary/20">
            <Zap className="w-5 h-5 text-primary" />
            <span className="text-sm font-medium">Autonomous Agents</span>
          </div>
          <div className="flex items-center gap-2 glass px-4 py-2 rounded-full border-primary/20">
            <Brain className="w-5 h-5 text-primary" />
            <span className="text-sm font-medium">AI-Powered Analysis</span>
          </div>
        </div>

        {/* Enhanced CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          <Button
            asChild
            size="lg"
            className="gradient-primary hover-glow-primary btn-glow text-lg px-8 h-14"
          >
            <Link href="/login">
              Login to Dashboard
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
          </Button>
          <Button
            asChild
            variant="outline"
            size="lg"
            className="glass hover-glow-accent text-lg px-8 h-14 border-primary/30"
          >
            <Link href="#how-it-works">View Demo</Link>
          </Button>
        </div>

        {/* Enhanced Trust Indicator */}
        <p className="text-sm text-muted-foreground">
          Built on enterprise-grade infrastructure
        </p>
      </div>

      {/* Enhanced Bottom Gradient Fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background via-background/80 to-transparent"></div>
    </section>
  );
}
