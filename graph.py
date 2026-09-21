"""Build the LangGraph StateGraph.

This is the orchestration layer. Each node is a plain function (state -> partial state).
Edges decide what runs next. A conditional edge demonstrates non-linear control flow:
if we can't understand the destination, we stop and ask the user instead of crashing.
"""
from __future__ import annotations
import re
from langgraph.graph import StateGraph, END
from state import TravelState
from tools import fetch_weather, search_attractions, search_hotels


# ---------- nodes ----------

def parse_input(state: TravelState) -> dict:
    """Deterministic stand-in for an LLM call. Parses 'N days in <city>, <budget>'.

    Swap this node for a ChatOpenAI + structured-output call to make it LLM-driven.
    The rest of the graph stays identical.
    """
    text = (state.get("raw_input") or "").lower()

    m_days = re.search(r"(\d+)\s*days?", text)
    days = int(m_days.group(1)) if m_days else 3

    m_budget = re.search(r"(budget|mid-range|luxury)", text)
    budget = m_budget.group(1) if m_budget else "mid-range"

    # crude destination extraction: text after "in" up to a comma
    m_city = re.search(r"in\s+([a-z\s]+?)(?:,|$)", text)
    destination = m_city.group(1).strip() if m_city else None

    if not destination:
        return {
            "needs_clarification": True,
            "clarification_question": "Which city would you like to visit?",
        }

    return {
        "destination": destination,
        "days": days,
        "budget": budget,
        "needs_clarification": False,
    }


def fetch_weather_node(state: TravelState) -> dict:
    return {"weather": fetch_weather(state["destination"])}


def search_attractions_node(state: TravelState) -> dict:
    return {"attractions": search_attractions(state["destination"])}


def search_hotels_node(state: TravelState) -> dict:
    return {"hotels": search_hotels(state["destination"], state.get("budget", "mid-range"))}


def build_itinerary(state: TravelState) -> dict:
    """Synthesize the final day-by-day plan from the tool results."""
    attractions = state.get("attractions", [])
    days = state.get("days", 3)
    per_day = max(1, len(attractions) // days) or 1

    itinerary = []
    idx = 0
    for d in range(1, days + 1):
        day_attractions = attractions[idx: idx + per_day]
        idx += per_day
        itinerary.append({
            "day": d,
            "focus": day_attractions[0]["type"] if day_attractions else "free",
            "items": [a["name"] for a in day_attractions],
        })
    return {"itinerary": itinerary}


# ---------- conditional routing ----------

def route_after_parse(state: TravelState) -> str:
    """If we couldn't parse a destination, end early with a clarification question."""
    if state.get("needs_clarification"):
        return "clarify"
    return "continue"


# ---------- assemble graph ----------

def build_graph():
    g = StateGraph(TravelState)

    g.add_node("parse_input", parse_input)
    g.add_node("fetch_weather", fetch_weather_node)
    g.add_node("search_attractions", search_attractions_node)
    g.add_node("search_hotels", search_hotels_node)
    g.add_node("build_itinerary", build_itinerary)

    g.set_entry_point("parse_input")

    # conditional edge: clarify OR continue down the pipeline
    g.add_conditional_edges(
        "parse_input",
        route_after_parse,
        {"clarify": END, "continue": "fetch_weather"},
    )

    g.add_edge("fetch_weather", "search_attractions")
    g.add_edge("search_attractions", "search_hotels")
    g.add_edge("search_hotels", "build_itinerary")
    g.add_edge("build_itinerary", END)

    return g.compile()
