"use client";

import { Network, Shield, Cpu, Database } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const architectureComponents = [
  {
    icon: Network,
    title: "Fetch.ai Autonomous Agents",
    description:
      "Intelligent agents that autonomously process financial documents, perform reconciliations, and execute complex accounting workflows without human intervention.",
    details:
      "Multi-agent coordination, natural language processing, automated decision making",
  },
  {
    icon: Shield,
    title: "Sui Blockchain Infrastructure",
    description:
      "Built on Sui's high-performance blockchain for secure, scalable, and lightning-fast transaction processing with advanced cryptographic security.",
    details: "Move programming language, parallel execution, instant finality",
  },
  {
    icon: Cpu,
    title: "AI-Powered Data Processing",
    description:
      "Advanced machine learning models analyze financial patterns, detect anomalies, and provide intelligent insights for better financial decision-making.",
    details: "Pattern recognition, anomaly detection, predictive analytics",
  },
  {
    icon: Database,
    title: "Decentralized Data Flow",
    description:
      "Secure data pipeline ensures information flows seamlessly from source systems to blockchain storage while maintaining privacy and compliance.",
    details: "End-to-end encryption, data integrity verification, audit trails",
  },
];

export default function Architecture() {
  return (
    <section className="py-24 bg-muted/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight mb-6">
            <span className="text-foreground">Technical</span>
            <br />
            <span className="text-foreground">Architecture</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Built on cutting-edge technology stack combining autonomous AI
            agents with blockchain infrastructure for maximum security and
            efficiency.
          </p>
        </div>

        {/* Architecture Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {architectureComponents.map((component) => {
            const IconComponent = component.icon;
            return (
              <Card
                key={component.title}
                className="glass hover-glow-primary transition-all duration-300 group"
              >
                <CardContent className="p-8">
                  {/* Icon */}
                  <div className="w-16 h-16 gradient-primary rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                    <IconComponent className="w-8 h-8 text-primary-foreground" />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-semibold mb-4 text-foreground">
                    {component.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed mb-4">
                    {component.description}
                  </p>

                  {/* Technical Details */}
                  <div className="pt-4 border-t border-border/50">
                    <p className="text-sm text-muted-foreground font-medium">
                      {component.details}
                    </p>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Architecture Flow Diagram */}
        <div className="mt-16 text-center">
          <div className="gradient-card rounded-2xl p-8 max-w-4xl mx-auto">
            <h3 className="text-2xl font-semibold mb-6 text-foreground">
              Data Flow Architecture
            </h3>
            <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8">
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 gradient-primary rounded-full flex items-center justify-center mb-2">
                  <Database className="w-6 h-6 text-primary-foreground" />
                </div>
                <span className="text-sm font-medium">Data Sources</span>
              </div>
              <div className="hidden md:block text-muted-foreground">→</div>
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 gradient-primary rounded-full flex items-center justify-center mb-2">
                  <Cpu className="w-6 h-6 text-primary-foreground" />
                </div>
                <span className="text-sm font-medium">AI Processing</span>
              </div>
              <div className="hidden md:block text-muted-foreground">→</div>
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 gradient-primary rounded-full flex items-center justify-center mb-2">
                  <Shield className="w-6 h-6 text-primary-foreground" />
                </div>
                <span className="text-sm font-medium">Blockchain Storage</span>
              </div>
              <div className="hidden md:block text-muted-foreground">→</div>
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 gradient-primary rounded-full flex items-center justify-center mb-2">
                  <Network className="w-6 h-6 text-primary-foreground" />
                </div>
                <span className="text-sm font-medium">
                  Analytics & Insights
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
