/**
 * Convert ISO 3166-1 alpha-2 country code to flag emoji.
 *
 * Algorithm: Each character in the code is offset by 0x1F1E6 to get
 * the regional indicator symbol. Two letters form the flag emoji.
 *
 * Example: "CN" -> 🇨🇳
 * Fallback: "XX" or invalid -> 🏳️
 *
 * Per Pitfall 4 in RESEARCH.md: Provide fallback for platforms
 * that don't support regional indicator symbols.
 */
export function countryCodeToFlag(code: string): string {
  if (!code || code.length !== 2) {
    return '🏳️'; // Fallback white flag
  }
  const base = 0x1f1e6; // Regional indicator A (maps 'A' to regional indicator A)
  const char1 = String.fromCodePoint(base + (code.charCodeAt(0) - 65));
  const char2 = String.fromCodePoint(base + (code.charCodeAt(1) - 65));
  return char1 + char2;
}