"""CLI entry: run the graph and print the synthesized itinerary."""
from __future__ import annotations
import sys
import json
from graph import build_graph


def run(request: str) -> None:
    app = build_graph()
    print(f"\n> Request: {request}\n" + "-" * 60)

    final = app.invoke({"raw_input": request})

    if final.get("needs_clarification"):
        print(f"[agent] Needs clarification: {final['clarification_question']}")
        return

    print(f"Destination : {final['destination']}")
    print(f"Budget      : {final.get('budget')}")
    print(f"Weather     : {final.get('weather')}")
    print(f"Hotels      : {[h['name'] for h in final.get('hotels', [])]}")
    print("\nItinerary:")
    for day in final.get("itinerary", []):
        print(f"  Day {day['day']} ({day['focus']}): {', '.join(day['items'])}")
    print("-" * 60 + "\n")


if __name__ == "__main__":
    req = " ".join(sys.argv[1:]) or "3 days in Kuala Lumpur, mid-range budget"
    run(req)
