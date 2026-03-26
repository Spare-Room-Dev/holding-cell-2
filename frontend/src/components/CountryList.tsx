'use client';

import { countryCodeToFlag } from '@/utils/countryToFlag';

interface CountryListProps {
  countries: [string, number][];  // [countryCode, count] pairs, already sorted
}

// Country code to name lookup (ISO 3166-1) - common countries only
const COUNTRY_NAMES: Record<string, string> = {
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

function getCountryName(code: string): string {
  return COUNTRY_NAMES[code] || code;
}

export function CountryList({ countries }: CountryListProps) {
  if (countries.length === 0) {
    return (
      <div className="flex flex-col items-center gap-xs">
        <span className="counter-label">Top Countries</span>
        <span className="text-text-muted text-sm">No attacks yet</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-xs">
      <span className="counter-label">Top Countries</span>
      <div className="flex flex-col gap-2xs">
        {countries.map(([code, count]) => (
          <div
            key={code}
            className="flex items-center gap-xs text-sm font-mono"
          >
            <span className="text-lg">{countryCodeToFlag(code)}</span>
            <span className="text-text-muted">
              {getCountryName(code)}
            </span>
            <span className="text-primary font-mono">
              {count.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}