# Tibbi — Front of House / Sales

Implemented: policy-gated, audited read-only product/availability presentation.
Capability: `front_of_house:product_offer:read`. Tibbi receives same-request,
same-actor/business audited recipe and stock results through the workflow. He does
not read other domains’ files. Prices and saleability remain explicitly unknown.

Tibbi owns customer-facing sales presentation; Ivy owns enquiries/order capture,
Bobathan owns physical inventory, Recipes owns product specifications, Saul owns
money, Galgali owns timing and Toby owns cross-domain decisions. No writes, order
acceptance, communications or stock reservation are implemented.

See docs/LOCAL_BROWNIE_FOUNDATIONS.md for the offline example and exact limits.
