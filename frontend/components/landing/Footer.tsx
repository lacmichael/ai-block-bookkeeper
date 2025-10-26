"use client";

import Link from "next/link";
import { Github, X, Linkedin, Mail } from "lucide-react";

const footerLinks = {
  product: [
    { name: "Features", href: "#features" },
    { name: "How It Works", href: "#how-it-works" },
    { name: "Architecture", href: "#architecture" },
    { name: "Use Cases", href: "#use-cases" },
    { name: "Pricing", href: "/pricing" },
  ],
  company: [
    { name: "About Us", href: "/about" },
    { name: "Careers", href: "/careers" },
    { name: "Blog", href: "/blog" },
    { name: "Press", href: "/press" },
    { name: "Contact", href: "/contact" },
  ],
  resources: [
    { name: "Documentation", href: "/docs" },
    { name: "API Reference", href: "/api" },
    { name: "Help Center", href: "/help" },
    { name: "Community", href: "/community" },
    { name: "Status", href: "/status" },
  ],
  legal: [
    { name: "Privacy Policy", href: "/privacy" },
    { name: "Terms of Service", href: "/terms" },
    { name: "Cookie Policy", href: "/cookies" },
    { name: "GDPR", href: "/gdpr" },
    { name: "Security", href: "/security" },
  ],
};

const socialLinks = [
  { name: "GitHub", href: "https://github.com/ascendtech", icon: Github },
  { name: "X", href: "https://x.com/ascendtech", icon: X },
  {
    name: "LinkedIn",
    href: "https://linkedin.com/company/ascendtech",
    icon: Linkedin,
  },
  { name: "Email", href: "mailto:hello@ascendtech.com", icon: Mail },
];

export default function Footer() {
  return (
    <footer className="bg-background py-16 border-t border-border/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-5 gap-12">
        {/* Brand Section */}
        <div className="md:col-span-2">
          <Link href="/" className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 gradient-primary rounded-lg flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-lg">
                A
              </span>
            </div>
            <span className="text-2xl font-bold text-foreground">
              AscendTech
            </span>
          </Link>
          <p className="text-muted-foreground mb-6 max-w-md">
            Revolutionizing financial operations with autonomous blockchain
            accounting. Powered by Fetch.ai agents and Sui blockchain
            technology.
          </p>
          <div className="flex gap-4">
            {socialLinks.map((social) => {
              const IconComponent = social.icon;
              return (
                <a
                  key={social.name}
                  href={social.href}
                  className="w-10 h-10 glass rounded-lg flex items-center justify-center hover-glow-accent transition-all duration-300"
                  aria-label={social.name}
                >
                  <IconComponent className="w-5 h-5 text-muted-foreground hover:text-foreground transition-colors" />
                </a>
              );
            })}
          </div>
        </div>

        {/* Product Links */}
        <div>
          <h3 className="font-semibold text-foreground mb-4">Product</h3>
          <ul className="space-y-3">
            {footerLinks.product.map((link) => (
              <li key={link.name}>
                <Link
                  href={link.href}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  {link.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Company Links */}
        <div>
          <h3 className="font-semibold text-foreground mb-4">Company</h3>
          <ul className="space-y-3">
            {footerLinks.company.map((link) => (
              <li key={link.name}>
                <Link
                  href={link.href}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  {link.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Resources & Legal */}
        <div>
          <h3 className="font-semibold text-foreground mb-4">Resources</h3>
          <ul className="space-y-3 mb-6">
            {footerLinks.resources.map((link) => (
              <li key={link.name}>
                <Link
                  href={link.href}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  {link.name}
                </Link>
              </li>
            ))}
          </ul>
          <h3 className="font-semibold text-foreground mb-4">Legal</h3>
          <ul className="space-y-3">
            {footerLinks.legal.map((link) => (
              <li key={link.name}>
                <Link
                  href={link.href}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  {link.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="mt-16 text-center text-sm text-muted-foreground">
        &copy; {new Date().getFullYear()} AscendTech. All rights reserved.
      </div>
    </footer>
  );
}
