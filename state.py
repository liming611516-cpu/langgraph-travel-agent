"""Typed state that flows through the LangGraph nodes.

Every node reads from and returns a partial update to this state. LangGraph merges
partial updates into the shared blackboard — this is the core pattern that lets
multi-agent systems coordinate across long-running tasks.
"""
from __future__ import annotations
from typing import TypedDict, List, Dict, Optional


class TravelState(TypedDict, total=False):
    # user request
    raw_input: str
    destination: Optional[str]
    days: Optional[int]
    budget: Optional[str]            # "budget" | "mid-range" | "luxury"

    # tool results
    weather: Optional[Dict]
    attractions: Optional[List[Dict]]
    hotels: Optional[List[Dict]]

    # final output
    itinerary: Optional[List[Dict]]

    # control flow
    needs_clarification: bool
    clarification_question: Optional[str]
