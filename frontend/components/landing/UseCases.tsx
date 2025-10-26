"use client";

import {
  Building2,
  Users,
  TrendingUp,
  Shield,
  FileText,
  Calculator,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const useCases = [
  {
    icon: Building2,
    title: "Enterprise Accounting",
    description:
      "Large corporations benefit from automated reconciliation, real-time financial reporting, and immutable audit trails for regulatory compliance.",
    benefits: [
      "Automated reconciliation",
      "Real-time reporting",
      "Regulatory compliance",
    ],
  },
  {
    icon: Users,
    title: "Small Business Management",
    description:
      "Small businesses streamline their financial operations with AI-powered bookkeeping, expense tracking, and automated invoice processing.",
    benefits: ["AI bookkeeping", "Expense tracking", "Invoice automation"],
  },
  {
    icon: TrendingUp,
    title: "Investment Firms",
    description:
      "Investment firms leverage blockchain technology for transparent portfolio management, automated compliance reporting, and secure transaction records.",
    benefits: [
      "Portfolio transparency",
      "Compliance automation",
      "Secure records",
    ],
  },
  {
    icon: Shield,
    title: "Financial Auditing",
    description:
      "Audit firms utilize immutable blockchain records and AI analysis to provide more accurate, efficient, and trustworthy audit services.",
    benefits: ["Immutable records", "AI analysis", "Enhanced accuracy"],
  },
  {
    icon: FileText,
    title: "Tax Preparation",
    description:
      "Tax professionals access comprehensive financial data with cryptographic verification, ensuring accuracy and reducing preparation time.",
    benefits: [
      "Comprehensive data",
      "Cryptographic verification",
      "Reduced prep time",
    ],
  },
  {
    icon: Calculator,
    title: "Financial Consulting",
    description:
      "Consultants provide data-driven insights using real-time analytics and predictive modeling powered by blockchain-verified financial data.",
    benefits: [
      "Real-time analytics",
      "Predictive modeling",
      "Data-driven insights",
    ],
  },
];

export default function UseCases() {
  return (
    <section className="py-24 bg-muted/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight mb-6">
            <span className="text-foreground">Real-World</span>
            <br />
            <span className="text-foreground">Applications</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Discover how organizations across industries are transforming their
            financial operations with our blockchain-powered accounting
            platform.
          </p>
        </div>

        {/* Use Cases Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {useCases.map((useCase) => {
            const IconComponent = useCase.icon;
            return (
              <Card
                key={useCase.title}
                className="glass hover-glow-primary transition-all duration-300 group h-full"
              >
                <CardContent className="p-8">
                  {/* Icon */}
                  <div className="w-16 h-16 gradient-primary rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                    <IconComponent className="w-8 h-8 text-primary-foreground" />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-semibold mb-4 text-foreground">
                    {useCase.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed mb-6">
                    {useCase.description}
                  </p>

                  {/* Benefits List */}
                  <div className="space-y-2">
                    {useCase.benefits.map((benefit) => (
                      <div key={benefit} className="flex items-center gap-2">
                        <div className="w-2 h-2 gradient-primary rounded-full"></div>
                        <span className="text-sm text-muted-foreground">
                          {benefit}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

      </div>
    </section>
  );
}
