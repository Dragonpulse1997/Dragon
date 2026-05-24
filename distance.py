#!/usr/bin/env python3
"""Measure distance between two locations by online address lookup."""

from __future__ import annotations

import argparse
import json
import math
import urllib.parse
import urllib.request

EARTH_RADIUS_KM = 6371.0
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"


class AddressLookupError(RuntimeError):
    """Raised when an address cannot be resolved."""


def geocode_address(address: str) -> tuple[float, float]:
    if not address.strip():
        raise AddressLookupError("Address cannot be empty.")

    params = urllib.parse.urlencode({"q": address, "format": "json", "limit": 1})
    request = urllib.request.Request(
        f"{NOMINATIM_SEARCH_URL}?{params}",
        headers={"User-Agent": "DragonDistance/1.0 (https://github.com/Dragonpulse1997/Dragon/issues)"},
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except Exception as exc:  # pragma: no cover - network/system errors
        raise AddressLookupError(f"Unable to look up address '{address}': {exc}") from exc

    if not payload:
        raise AddressLookupError(f"No coordinates found for address: {address}")

    result = payload[0]
    return float(result["lat"]), float(result["lon"])


def haversine_km(start: tuple[float, float], end: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, start)
    lat2, lon2 = map(math.radians, end)
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def calculate_distance_km(from_address: str, to_address: str) -> float:
    return haversine_km(geocode_address(from_address), geocode_address(to_address))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Measure distance between two addresses")
    parser.add_argument("from_address", help="Starting address")
    parser.add_argument("to_address", help="Destination address")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        distance_km = calculate_distance_km(args.from_address, args.to_address)
    except AddressLookupError as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Distance between locations: {distance_km:.2f} km")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
