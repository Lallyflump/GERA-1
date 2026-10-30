# Project brief

## Problem and outcome
Small-business information is split across orders, ingredients, cash, diaries, recipes and paperwork. GERA-1 should reduce the owner's coordination burden by joining this information into useful, traceable decisions without letting individual specialists exceed their authority.

Reference business: A Moment of Escape Ltd / Lisa's Little Bakery. Other businesses should be supported through business profiles, policies and adapters rather than bakery-specific assumptions embedded in Toby.

## Foundation requirements
Ten defined strands; Toby as Nemotron-powered orchestrator; restricted specialists; overall business visibility for Toby; Python direction; incremental delivery; RAG for document evidence. Tavily and Nebius are candidate integrations, not mandatory dependencies. This project is intended for an NVIDIA agentic/RAG hackathon, whose exact event, current rules and deadline have not been supplied or verified here.

## First prototype scope (proposed)
One business, one operator, one order-feasibility journey, synthetic fixtures, read-only specialist checks and a traceable recommendation. Recipe evidence exercises RAG. Later milestones add explicitly approved writes and optional live research.

## Deferred
Full autonomous operations, payments, bulk marketing, public customer portal, production compliance assurance, forecasting without historical data, all ten independent deployed agents and multi-business production hosting.

## Success
The owner can understand whether an order is feasible, what evidence supports that conclusion, what is unknown and which next actions require a decision. A rejected permission request cannot mutate another domain. Repeating an approved action cannot create duplicate orders or expenses.

## Setup boundary
Lisa supplied the continuation of the setup brief: keep the architecture modular, distinguish confirmed decisions from exploration, create a journal and technology notes, and stop before implementing the next step. These requirements are incorporated in this foundation.
