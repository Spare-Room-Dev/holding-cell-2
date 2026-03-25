// frontend/src/components/ThemeToggle.tsx
'use client';

import { useState, useEffect } from 'react';

/**
 * Theme toggle for light/dark mode switching.
 * Dark mode is default. Light mode is activated by adding .light class to <html>.
 * No localStorage persistence - resets to dark on each page load.
 */
export function ThemeToggle() {
  const [isDark, setIsDark] = useState(true); // Dark mode is default

  useEffect(() => {
    const html = document.documentElement;

    // Toggle .light class: add for light mode, remove for dark mode
    html.classList.toggle('light', !isDark);

    // Ensure .dark class is always present for Tailwind dark: variants
    if (!html.classList.contains('dark')) {
      html.classList.add('dark');
    }
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark((prev) => !prev);
  };

  return (
    <button
      onClick={toggleTheme}
      className="p-sm rounded-md hover:bg-surface-raised transition-colors"
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      type="button"
    >
      {isDark ? (
        // Sun icon (shown when in dark mode - click to switch to light)
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          className="w-5 h-5 text-text-muted"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
      ) : (
        // Moon icon (shown when in light mode - click to switch to dark)
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          className="w-5 h-5 text-text-muted"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
          />
        </svg>
      )}
    </button>
  );
}