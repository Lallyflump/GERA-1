# Specialist strands

All ten agreed strands are retained. Saul, Galgali, Bobathan, Tibbi and Recipes/Product Library have bounded local read capabilities; the remaining strands are architectural placeholders. Unnamed strands retain descriptive titles.

| ID | Strand | Agent | Owned responsibility |
| --- | --- | --- | --- |
| `inventory` | Back of House Inventory | Bobathan | Ingredients, tea, coffee, packaging and stock. |
| `reception` | Reception | Ivy | Customer enquiries, bookings and order capture. |
| `finance` | Finance | Saul | Ledger, income, expenses, cashflow, monetary commitment details and affordability. |
| `operations` | Time & Operations | Galgali | Baking/opening/cleaning days, deliveries, events, tasks and calendar timing for expected incoming/outgoing bills. |
| `front_of_house` | Front of House / Sales | Tibbi | Evidenced customer-facing product offers and availability presentation; seating/displays remain future work. |
| `admin_compliance` | Admin & Compliance | Not assigned | Insurance, tax dates, certificates, supplier records and administration. |
| `provenance` | Provenance & Traceability | Not assigned | Source provenance, batch records, recalls, local sourcing and sustainability evidence. |
| `recipes` | Recipes & Product Library | Not assigned | Recipes, allergens, batch costs, labels and specifications. |
| `marketing` | Marketing & Newsletter | Montgomery | Seasonal content drafts from supplied public research; no publication capability. |
| `analytics` | Analytics & Forecasting | Not assigned | Sales, seasons, weather/school/event effects and newsletter performance. |

Toby coordinates all strands and does not own their underlying records. See DATA_AND_RAG.md for shared-record boundaries and GOVERNANCE.md for execution authority.

Percival is the optional public-research specialist, outside the ten business-domain
strands. His first bounded capability is the fixed Halloween customs search described
in [local Toby interface instructions](LOCAL_TOBY_INTERFACE.md). It cannot establish
facts about the bakery's actual ingredients, suppliers or provenance.

For a scheduled incoming or outgoing bill, Galgali owns **when it appears on the calendar** and stores a reference to the finance record. Saul owns **the money facts**: amount, direction, category and paid/received status. Toby combines both views when a decision depends on timing and money.

Finished-product physical stock belongs to Bobathan; Tibbi presents its authorized view.
The brownie-order tentacle coordinates on Toby’s behalf without acquiring domain
ownership. See [local foundations](LOCAL_BROWNIE_FOUNDATIONS.md).
