# ADR 0001 — Modular application with domain-owned tools

Date: 18 September 2026. Status: proposed implementation direction.

Context: GERA-1 needs ten bounded business strands and a central reasoning agent, while remaining small enough to build and inspect incrementally.

Decision: start with one modular Python application, typed tool boundaries, application-enforced permissions and replaceable model/storage adapters. Toby coordinates; domain owners perform writes. Use structured data for mutable facts and RAG for document evidence. Keep business identity and policies in configuration.

Alternatives: ten separately deployed agents add early operational complexity; a single unbounded assistant obscures ownership. A framework may help later but is not a foundation prerequisite.

Consequences: lower setup overhead and easier end-to-end inspection; permission enforcement remains necessary inside a shared process. Distributed deployment, vector database and cloud provider selection are deferred. Revisit once the working slice exposes a concrete need or official hackathon rules require a change.
