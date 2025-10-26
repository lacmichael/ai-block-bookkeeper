"use client";

import { Party } from "@/lib/actions/business-events";
import { Badge } from "@/components/ui/badge";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { User, Building, Mail, MapPin, Wallet } from "lucide-react";

interface PartyInfoProps {
  party: Party | null | undefined;
  role?: string | null;
  children: React.ReactNode;
}

export function PartyInfo({ party, role, children }: PartyInfoProps) {
  if (!party) {
    return <span className="text-muted-foreground">-</span>;
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" className="h-auto p-0 text-left justify-start">
          {children}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80">
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            {party.type === "CUSTOMER" || party.type === "VENDOR" ? (
              <Building className="h-4 w-4 text-muted-foreground" />
            ) : (
              <User className="h-4 w-4 text-muted-foreground" />
            )}
            <div>
              <h4 className="font-medium">{party.display_name}</h4>
              {party.legal_name && party.legal_name !== party.display_name && (
                <p className="text-sm text-muted-foreground">
                  {party.legal_name}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant="outline">{party.type}</Badge>
            {role && <Badge variant="secondary">{role}</Badge>}
          </div>

          {party.email && (
            <div className="flex items-center gap-2 text-sm">
              <Mail className="h-4 w-4 text-muted-foreground" />
              <span>{party.email}</span>
            </div>
          )}

          {(party.street || party.city || party.state || party.postal_code) && (
            <div className="flex items-start gap-2 text-sm">
              <MapPin className="h-4 w-4 text-muted-foreground mt-0.5" />
              <div>
                {party.street && <div>{party.street}</div>}
                {(party.city || party.state || party.postal_code) && (
                  <div>
                    {party.city && party.state && party.postal_code
                      ? `${party.city}, ${party.state} ${party.postal_code}`
                      : party.city || party.state || party.postal_code}
                  </div>
                )}
                {party.country && <div>{party.country}</div>}
              </div>
            </div>
          )}

          {party.sui_address && (
            <div className="flex items-center gap-2 text-sm">
              <Wallet className="h-4 w-4 text-muted-foreground" />
              <span className="font-mono text-xs break-all">
                {party.sui_address}
              </span>
            </div>
          )}

          <div className="pt-2 border-t">
            <p className="text-xs text-muted-foreground">
              Party ID: {party.party_id}
            </p>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
