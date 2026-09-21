# langgraph-travel-agent

A minimal but complete **multi-node LangGraph state-graph demo** that turns a one-line
travel request into a day-by-day itinerary. Built to show the same pattern used in
production multi-agent systems (planning → tool calls → synthesis), but self-contained
and runnable with **no API key**.

> This is a personal technical demo that reconstructs the architecture pattern from a
> team project (SynTour, APICTA 2025 四强). It is not the production code — it is a
> clean, readable reference implementation of a LangGraph workflow.

## What it demonstrates

- **StateGraph** with typed state (`TypedDict`) — the backbone of every LangGraph app.
- **5 nodes** chained by edges: `parse_input → fetch_weather → search_attractions →
  search_hotels → build_itinerary`.
- **Conditional edges**: if the destination is unknown, the graph loops back to ask
  for clarification (showing real control flow, not just a linear pipeline).
- **Tool layer**: each node calls a mock tool (weather / attractions / hotels) that
  stands in for a real external API (OpenWeather / Geoapify / Amadeus).
- **Pluggable "LLM"**: the parser/planner uses deterministic rules by default so the
  demo runs offline; swap in `ChatOpenAI` to make it LLM-driven.

## Quick start

```bash
cd langgraph-travel-agent
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py "3 days in Kuala Lumpur, mid-range budget"
```

You should see the graph run node-by-node and print a synthesized itinerary.

## Architecture

```
parse_input ──► fetch_weather ──► search_attractions ──► search_hotels ──► build_itinerary
     │                                                                            ▲
     └────────── (destination unknown: ask user, re-enter) ─────────────────────┘
```

State object flows through every node; each node returns a partial update that LangGraph
merges. This is exactly the "shared blackboard" pattern that lets multi-agent systems
stay coordinated across long-running tasks.

## Layout

```
langgraph_travel_agent/
├── state.py      # TypedDict graph state
├── tools.py      # Mock external API calls (weather/attractions/hotels)
├── graph.py      # StateGraph construction + edges
└── main.py       # CLI entry, runs the graph and prints the itinerary
```

## Swapping in a real LLM

Replace the deterministic `parse_input` logic in `graph.py` with a
`langchain_openai.ChatOpenAI` bound to a structured-output tool. The graph structure
and tool layer stay the same — this is the same separation between **orchestration**
and **model reasoning** that production agent systems rely on.
