"use server";

import { createClient } from "@/utils/supabase/server";
import { mockBusinessEvents } from "@/utils/mockData";

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

// Helper function to generate realistic party display names
function getPartyDisplayName(partyId: string, role: string): string {
  const partyNames: Record<string, string> = {
    party_customer_001: "Acme Corp",
    party_customer_002: "TechStart Inc",
    party_customer_003: "Global Solutions Ltd",
    party_customer_004: "Innovation Hub",
    party_customer_005: "Digital Ventures",
    party_vendor_001: "WebDev Solutions",
    party_vendor_002: "Office Space LLC",
    party_vendor_003: "Software Licensing Co",
    party_vendor_004: "Utility Services Inc",
    party_employee_001: "John Smith",
    party_internal_001: "Internal Account",
  };

  return partyNames[partyId] || `${role} ${partyId.split("_").pop()}`;
}

// Helper function to get mock business events
function getMockBusinessEvents(): BusinessEvent[] {
  return mockBusinessEvents.map((event) => ({
    event_id: event.event_id,
    source_system: event.source_system,
    source_id: event.source_id,
    occurred_at: event.occurred_at,
    recorded_at: event.recorded_at,
    event_kind: event.event_kind,
    amount_minor: event.amount_minor,
    currency: event.currency,
    description: event.description,
    dedupe_key: `mock_${event.event_id}`,
    payer_party_id: event.payer?.party_id || null,
    payer_role: event.payer?.role || null,
    payee_party_id: event.payee?.party_id || null,
    payee_role: event.payee?.role || null,
    payer_party: event.payer
      ? ({
          party_id: event.payer.party_id,
          display_name: getPartyDisplayName(
            event.payer.party_id,
            event.payer.role
          ),
          type: event.payer.role,
          sui_address: `0x${Math.random().toString(16).substr(2, 40)}`,
        } as Party)
      : null,
    payee_party: event.payee
      ? ({
          party_id: event.payee.party_id,
          display_name: getPartyDisplayName(
            event.payee.party_id,
            event.payee.role
          ),
          type: event.payee.role,
          sui_address: `0x${Math.random().toString(16).substr(2, 40)}`,
        } as Party)
      : null,
    processing: {
      state: event.processing.state,
      last_error: event.processing.last_error || null,
    },
    reconciliation_state: event.reconciliation_state,
  }));
}

// Helper function to fetch party details
async function getPartyById(partyId: string): Promise<Party | null> {
  const supabase = await createClient();

  try {
    const { data, error } = await supabase
      .from("parties")
      .select("*")
      .eq("party_id", partyId)
      .single();

    if (error) {
      console.error(`Error fetching party ${partyId}:`, error);
      // Return a fallback party object if the party doesn't exist in the database
      return {
        party_id: partyId,
        display_name: `Party ${partyId.split("_").pop()}`,
        type: "UNKNOWN",
        sui_address: `0x${Math.random().toString(16).substr(2, 40)}`,
      } as Party;
    }

    if (!data) {
      // Return a fallback party object if no data found
      return {
        party_id: partyId,
        display_name: `Party ${partyId.split("_").pop()}`,
        type: "UNKNOWN",
        sui_address: `0x${Math.random().toString(16).substr(2, 40)}`,
      } as Party;
    }

    return data as Party;
  } catch (error) {
    console.error(`Error fetching party ${partyId}:`, error);
    // Return a fallback party object on any error
    return {
      party_id: partyId,
      display_name: `Party ${partyId.split("_").pop()}`,
      type: "UNKNOWN",
      sui_address: `0x${Math.random().toString(16).substr(2, 40)}`,
    } as Party;
  }
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
        metadata
      `
      )
      .order("occurred_at", { ascending: false })
      .limit(50);

    if (error) {
      console.error("Error fetching business events:", error);
      // Fall back to mock data if database is empty or has errors
      return getMockBusinessEvents();
    }

    // If no data returned, use mock data
    if (!data || data.length === 0) {
      console.log("No data in database, using mock data");
      return getMockBusinessEvents();
    }

    // Transform the data and fetch party details
    const transformedData = await Promise.all(
      data.map(async (event: Record<string, unknown>) => {
        // Fetch payer and payee party details if IDs exist
        const payerParty = event.payer_party_id
          ? await getPartyById(event.payer_party_id as string)
          : null;

        const payeeParty = event.payee_party_id
          ? await getPartyById(event.payee_party_id as string)
          : null;

        return {
          event_id: event.event_id as string,
          source_system: event.source_system as string,
          source_id: event.source_id as string,
          occurred_at: event.occurred_at as string,
          recorded_at: event.recorded_at as string,
          event_kind: event.event_kind as string,
          amount_minor: event.amount_minor as number,
          currency: event.currency as string,
          description: event.description as string | null,
          dedupe_key: event.dedupe_key as string,
          payer_party_id: event.payer_party_id as string | null,
          payer_role: event.payer_role as string | null,
          payee_party_id: event.payee_party_id as string | null,
          payee_role: event.payee_role as string | null,
          payer_party: payerParty,
          payee_party: payeeParty,
          processing: {
            state: (event.processing_state as string) || "PENDING",
            last_error: (event.processing_last_error as string) || null,
          },
          reconciliation_state: "UNRECONCILED", // Default value since not in schema
        };
      })
    );

    return transformedData;
  } catch (error) {
    console.error("Error in getBusinessEvents:", error);
    // Fall back to mock data on any error
    return getMockBusinessEvents();
  }
}

export async function getBusinessEventById(
  eventId: string
): Promise<BusinessEvent | null> {
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
        metadata
      `
      )
      .eq("event_id", eventId)
      .single();

    if (error) {
      console.error("Error fetching business event:", error);
      // Fall back to mock data
      const mockEvents = getMockBusinessEvents();
      return mockEvents.find((event) => event.event_id === eventId) || null;
    }

    if (!data) {
      // Fall back to mock data
      const mockEvents = getMockBusinessEvents();
      return mockEvents.find((event) => event.event_id === eventId) || null;
    }

    // Fetch payer and payee party details if IDs exist
    const payerParty = data.payer_party_id
      ? await getPartyById(data.payer_party_id)
      : null;

    const payeeParty = data.payee_party_id
      ? await getPartyById(data.payee_party_id)
      : null;

    // Transform the data to match our interface
    const transformedData: BusinessEvent = {
      event_id: data.event_id,
      source_system: data.source_system,
      source_id: data.source_id,
      occurred_at: data.occurred_at,
      recorded_at: data.recorded_at,
      event_kind: data.event_kind,
      amount_minor: data.amount_minor,
      currency: data.currency,
      description: data.description,
      dedupe_key: data.dedupe_key,
      payer_party_id: data.payer_party_id,
      payer_role: data.payer_role,
      payee_party_id: data.payee_party_id,
      payee_role: data.payee_role,
      payer_party: payerParty,
      payee_party: payeeParty,
      processing: {
        state: data.processing_state || "PENDING",
        last_error: data.processing_last_error || null,
      },
      reconciliation_state: "UNRECONCILED", // Default value since not in schema
    };

    return transformedData;
  } catch (error) {
    console.error("Error in getBusinessEventById:", error);
    // Fall back to mock data
    const mockEvents = getMockBusinessEvents();
    return mockEvents.find((event) => event.event_id === eventId) || null;
  }
}
