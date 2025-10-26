"use client";

import { Shield, Database, Brain, Lock, BarChart3, Zap } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const features = [
  {
    icon: Shield,
    title: "Immutable Audit Trail",
    description:
      "Every transaction is permanently sealed by Sui blockchain consensus. Records cannot be altered or deleted, preventing internal fraud.",
  },
  {
    icon: Database,
    title: "Cryptographic Verification",
    description:
      "Leverage Sui's object-centric model for instant verification. Auditors bypass manual reconciliation with cryptographic proofs.",
  },
  {
    icon: Brain,
    title: "Autonomous AI Agents",
    description:
      "Fetch.ai agents handle data ingestion, normalization, and strategic analysis—no human intervention required.",
  },
  {
    icon: Lock,
    title: "Trustless Analysis",
    description:
      "Financial insights built on consensus-verified data, ensuring reports reflect absolute financial truth.",
  },
  {
    icon: BarChart3,
    title: "Real-Time Intelligence",
    description:
      "Natural language queries against your ledger. Ask complex questions, get instant AI-powered answers.",
  },
  {
    icon: Zap,
    title: "High-Volume Processing",
    description:
      "Built for scale. Handle thousands of transactions with autonomous reasoning and intelligent categorization.",
  },
];

export default function Features() {
  return (
    <section className="py-24 section-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight mb-6">
            <span className="text-foreground">Revolutionary</span>
            <br />
            <span className="text-foreground">Blockchain Accounting</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Experience the next generation of financial technology with our
            comprehensive suite of blockchain-powered accounting solutions.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature) => {
            const IconComponent = feature.icon;
            return (
              <Card
                key={feature.title}
                className="glass hover-glow-primary transition-all duration-300 group"
              >
                <CardContent className="p-8">
                  {/* Icon */}
                  <div className="w-16 h-16 gradient-primary rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                    <IconComponent className="w-8 h-8 text-primary-foreground" />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-semibold mb-4 text-foreground">
                    {feature.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}
