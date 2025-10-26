"use client";

import { FileText, RefreshCw, Database, BarChart } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const steps = [
  {
    number: 1,
    icon: FileText,
    title: "Data Ingestion",
    description:
      "Automatically capture and process financial documents from multiple sources including invoices, receipts, bank statements, and transaction records.",
  },
  {
    number: 2,
    icon: RefreshCw,
    title: "Secure Processing",
    description:
      "AI agents analyze and validate financial data, perform reconciliations, and ensure accuracy through advanced machine learning algorithms.",
  },
  {
    number: 3,
    icon: Database,
    title: "Immutable Storage",
    description:
      "Processed data is cryptographically secured and stored on the Sui blockchain, creating an unalterable audit trail for compliance and transparency.",
  },
  {
    number: 4,
    icon: BarChart,
    title: "AI Analysis",
    description:
      "Generate real-time insights, financial reports, and predictive analytics to help you make informed business decisions with confidence.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 section-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight mb-6">
            <span className="text-foreground">How It</span>
            <br />
            <span className="text-foreground">Works</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Our streamlined process transforms your financial operations in four
            simple steps, powered by cutting-edge AI and blockchain technology.
          </p>
        </div>

        {/* Process Flow */}
        <div className="gradient-card rounded-3xl p-8 md:p-12">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, index) => {
              const IconComponent = step.icon;
              const isLast = index === steps.length - 1;

              return (
                <div key={step.number} className="relative">
                  {/* Step Card */}
                  <Card className="glass hover-glow-primary transition-all duration-300 group h-full">
                    <CardContent className="p-6 text-center">
                      {/* Number Badge */}
                      <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                        <Badge className="gradient-primary text-primary-foreground font-bold text-lg w-8 h-8 rounded-full p-0 flex items-center justify-center">
                          {step.number}
                        </Badge>
                      </div>

                      {/* Icon */}
                      <div className="w-20 h-20 gradient-primary rounded-full flex items-center justify-center mx-auto mb-6 mt-4 group-hover:scale-110 transition-transform duration-300">
                        <IconComponent className="w-10 h-10 text-primary-foreground" />
                      </div>

                      {/* Content */}
                      <h3 className="text-xl font-semibold mb-4 text-foreground">
                        {step.title}
                      </h3>
                      <p className="text-muted-foreground leading-relaxed">
                        {step.description}
                      </p>
                    </CardContent>
                  </Card>

                  {/* Connecting Arrow */}
                  {!isLast && (
                    <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-10">
                      <div className="w-8 h-8 gradient-primary rounded-full flex items-center justify-center">
                        <svg
                          className="w-4 h-4 text-primary-foreground"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <p className="text-lg text-muted-foreground mb-6">
            Ready to transform your financial operations?
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/login"
              className="inline-flex items-center justify-center px-8 py-3 gradient-primary text-primary-foreground font-semibold rounded-lg hover-glow-primary transition-all duration-300"
            >
              Get Started Today
            </a>
            <a
              href="#features"
              className="inline-flex items-center justify-center px-8 py-3 glass text-foreground font-semibold rounded-lg hover-glow-accent transition-all duration-300"
            >
              Learn More
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
