/**
 * AttackEvent TypeScript interface
 * Must match backend Pydantic model in backend/models.py
 * Keep in sync manually (per D-10 to D-13)
 */

export type Archetype =
  | 'script_kiddie'
  | 'botnet_drone'
  | 'apt_operative'
  | 'iot_worm'
  | 'hacktivist';

export interface AttackEvent {
  /** UUID of the attack event */
  id: string;
  /** ISO 8601 timestamp */
  timestamp: string;
  /** IP address (e.g., "203.0.113.42") */
  ip: string;
  /** Country name (e.g., "China") */
  country: string;
  /** Country code (e.g., "CN") */
  countryCode: string;
  /** Port number (e.g., 22) */
  port: number;
  /** Protocol (e.g., "SSH") */
  protocol: string;
  /** Behavioral classification */
  archetype: Archetype;
  /** Commands attempted */
  commands: string[];
  /** Duration in seconds */
  duration: number;
  /** Original fake log line */
  rawLog: string;
}

export interface Analytics {
  countries: Record<string, number>;  // countryCode -> count
  protocols: Record<string, number>;  // SSH/TELNET -> count
  ports: Record<string, number>;       // port number -> count
}

export interface AttackHistoryPayload {
  attacks: AttackEvent[];
  lifetime_count: number;
  analytics: Analytics;
}

export interface CountryPrisoner {
  /** ISO 3166-1 alpha-2 country code (e.g., "CN") */
  countryCode: string;
  /** Human-readable country name (e.g., "China") */
  countryName: string;
  /** Total number of attacks from this country */
  count: number;
  /** Breakdown of attacks by archetype */
  archetypes: Partial<Record<Archetype, number>>;
  /** ISO 8601 timestamp of most recent attack */
  lastAttack: string;
  /** True only on the render where this country first appears */
  isNew: boolean;
  /** True when count increased and previous count was > 0 (not on first appearance) */
  isUpdated: boolean;
}