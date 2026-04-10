'use client';

import { countryCodeToFlag } from '@/utils/countryToFlag';
import { COUNTRY_NAMES, getCountryName } from '@/utils/countryNames';

interface CountryListProps {
  countries: [string, number][];  // [countryCode, count] pairs, already sorted
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