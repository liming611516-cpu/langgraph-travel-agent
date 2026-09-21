"""Mock external API calls.

In production these would be real API integrations (OpenWeather / Geoapify / Amadeus).
Here they return deterministic fixture data so the graph runs offline with no key.
The interface shape is what matters: each tool takes a destination + constraints and
returns a structured result that downstream nodes can consume.
"""
from __future__ import annotations
import random
from typing import Dict, List

# tiny fixture DB — in real code this is a REST call
_FIXTURE: Dict[str, Dict] = {
    "kuala lumpur": {
        "weather": {"temp_c": 32, "condition": "thunderstorm", "humidity": 82},
        "attractions": [
            {"name": "Petronas Twin Towers", "type": "sight", "duration_h": 2},
            {"name": "Batu Caves", "type": "nature", "duration_h": 3},
            {"name": "Jalan Alor Night Market", "type": "food", "duration_h": 2},
            {"name": "Merdeka Square", "type": "sight", "duration_h": 1.5},
        ],
        "hotels": [
            {"name": "Budget Inn Bukit Bintang", "tier": "budget", "price_usd": 28},
            {"name": "MidRange Pavilion Hotel", "tier": "mid-range", "price_usd": 75},
            {"name": "Luxury Mandarin Tower", "tier": "luxury", "price_usd": 220},
        ],
    },
    "bangkok": {
        "weather": {"temp_c": 34, "condition": "sunny", "humidity": 70},
        "attractions": [
            {"name": "Grand Palace", "type": "sight", "duration_h": 3},
            {"name": "Wat Arun", "type": "sight", "duration_h": 2},
            {"name": "Chatuchak Market", "type": "shopping", "duration_h": 3},
        ],
        "hotels": [
            {"name": "Backpacker Khao San", "tier": "budget", "price_usd": 18},
            {"name": "MidRange Sukhumvit", "tier": "mid-range", "price_usd": 60},
        ],
    },
}


def _known_destination(name: str) -> str | None:
    n = (name or "").strip().lower()
    for key in _FIXTURE:
        if key in n or n in key:
            return key
    return None


def fetch_weather(destination: str) -> Dict:
    """Mock weather API."""
    key = _known_destination(destination)
    if not key:
        return {"temp_c": 0, "condition": "unknown", "humidity": 0}
    return _FIXTURE[key]["weather"]


def search_attractions(destination: str) -> List[Dict]:
    key = _known_destination(destination)
    return _FIXTURE.get(key, {}).get("attractions", [])


def search_hotels(destination: str, budget: str) -> List[Dict]:
    key = _known_destination(destination)
    all_hotels = _FIXTURE.get(key, {}).get("hotels", [])
    if budget in ("budget", "mid-range", "luxury"):
        return [h for h in all_hotels if h["tier"] == budget] or all_hotels
    return all_hotels
