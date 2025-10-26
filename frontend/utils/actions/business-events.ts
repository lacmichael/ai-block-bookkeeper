"use server";

import { createClient } from "@/utils/supabase/server";

export interface Party {
  party_id: string;
  display_name: string;
  type: string;
  legal_name?: string;
  email?: string;
  street?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  sui_address?: string;
}

export interface BusinessEvent {
  event_id: string;
  source_system: string;
  source_id: string;
  occurred_at: string;
  recorded_at: string;
  event_kind: string;
  amount_minor: number;
  currency: string;
  description: string | null;
  dedupe_key: string;
  payer_party_id: string | null;
  payer_role: string | null;
  payee_party_id: string | null;
  payee_role: string | null;
  payer_party?: Party | null;
  payee_party?: Party | null;
  processing: {
    state: string;
    last_error: string | null;
  };
  reconciliation_state: string;
}

export async function getBusinessEvents(): Promise<BusinessEvent[]> {
  const supabase = await createClient();

  try {
    const { data, error } = await supabase
      .from("business_events")
      .select(
        `
        event_id,
        source_system,
        source_id,
        occurred_at,
        recorded_at,
        event_kind,
        amount_minor,
        currency,
        description,
        processing_state,
        processing_last_error,
        dedupe_key,
        payer_party_id,
        payer_role,
        payee_party_id,
        payee_role,
        metadata,
        payer_party:payer_party_id(
          party_id,
          display_name,
          type,
          legal_name,
          email,
          street,
          city,
          state,
          postal_code,
          country,
          sui_address
        ),
        payee_party:payee_party_id(
          party_id,
          display_name,
          type,
          legal_name,
          email,
          street,
          city,
          state,
          postal_code,
          country,
          sui_address
        )
      `
      )
      .order("occurred_at", { ascending: false })
      .limit(50);

    if (error) {
      console.error("Error fetching business events:", error);
      return [];
    }

    // Transform the data to match our interface
    const transformedData = (data || []).map((event: any) => ({
      event_id: event.event_id,
      source_system: event.source_system,
      source_id: event.source_id,
      occurred_at: event.occurred_at,
      recorded_at: event.recorded_at,
      event_kind: event.event_kind,
      amount_minor: event.amount_minor,
      currency: event.currency,
      description: event.description,
      dedupe_key: event.dedupe_key,
      payer_party_id: event.payer_party_id,
      payer_role: event.payer_role,
      payee_party_id: event.payee_party_id,
      payee_role: event.payee_role,
      payer_party: event.payer_party || null,
      payee_party: event.payee_party || null,
      processing: {
        state: event.processing_state || "PENDING",
        last_error: event.processing_last_error || null,
      },
      reconciliation_state: "UNRECONCILED", // Default value since not in schema
    }));

    return transformedData;
  } catch (error) {
    console.error("Error in getBusinessEvents:", error);
    return [];
  }
}
