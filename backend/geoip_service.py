"""
GeoIP service for IP-to-country enrichment.

Per D-20: MaxMind GeoLite2 database for country lookups
Per D-22: Country code derived from attacker IP, mapped to country name
Per D-23: Country code used for flag emoji display in frontend
"""

import os
from typing import Tuple, Optional

try:
    import geoip2.database
    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False


class GeoIPService:
    """
    MaxMind GeoLite2 country lookup service.

    Provides IP-to-country enrichment for attacker IPs.
    Fallback to ("Unknown", "XX") if database unavailable.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize GeoIP reader.

        Args:
            db_path: Path to GeoLite2-Country.mmdb
                     Defaults to GEOIP_DB_PATH env var or /geoip/GeoLite2-Country.mmdb
        """
        self.db_path = db_path or os.environ.get(
            "GEOIP_DB_PATH", "/geoip/GeoLite2-Country.mmdb"
        )
        self.reader = None

        if GEOIP_AVAILABLE:
            try:
                if os.path.exists(self.db_path):
                    self.reader = geoip2.database.Reader(self.db_path)
                    print(f"[GeoIP] Loaded database: {self.db_path}")
                else:
                    print(f"[GeoIP] Database not found at {self.db_path}, using fallback")
            except Exception as e:
                print(f"[GeoIP] Failed to load database: {e}, using fallback")
        else:
            print("[GeoIP] geoip2 library not installed, using fallback")

    def get_country(self, ip: str) -> Tuple[str, str]:
        """
        Get country name and code for an IP address.

        Args:
            ip: IP address string (e.g., "192.0.2.1")

        Returns:
            Tuple[str, str]: (country_name, country_code)
                             Returns ("Unknown", "XX") on failure
        """
        if self.reader is None:
            return ("Unknown", "XX")

        try:
            response = self.reader.country(ip)
            return (
                response.country.name or "Unknown",
                response.country.iso_code or "XX"
            )
        except Exception as e:
            # IP not in database, private IP, or lookup error
            return ("Unknown", "XX")

    def close(self):
        """Close the GeoIP reader."""
        if self.reader:
            self.reader.close()

    def __del__(self):
        self.close()