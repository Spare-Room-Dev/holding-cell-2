/**
 * Shared country code to name mapping (ISO 3166-1 alpha-2).
 * Used by CountryList, CountryTooltip, and useCountryPrisoners hook.
 * Per D-09: CountryList uses this shared constant instead of a local copy.
 */

export const COUNTRY_NAMES: Record<string, string> = {
  CN: 'China',
  RU: 'Russia',
  US: 'United States',
  BR: 'Brazil',
  IR: 'Iran',
  IN: 'India',
  KR: 'South Korea',
  VN: 'Vietnam',
  ID: 'Indonesia',
  TR: 'Turkey',
  TW: 'Taiwan',
  JP: 'Japan',
  DE: 'Germany',
  GB: 'United Kingdom',
  FR: 'France',
  NL: 'Netherlands',
  UA: 'Ukraine',
  // Add more as needed
};

/**
 * Get the display name for a country code.
 * Falls back to the raw code if no mapping exists.
 */
export function getCountryName(code: string): string {
  return COUNTRY_NAMES[code] || code;
}