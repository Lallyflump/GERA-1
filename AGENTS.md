# GERA-1 development guidance

Read README.md, docs/STATUS.md, docs/BUILD_PLAN.md and the relevant architecture documents before changing the project.

- Preserve GERA-1's spelling and full name. Gerald is the codename; Toby is the orchestrator.
- Retain Saul, Galgali, Bobathan and Ivy in their agreed roles.
- Build one milestone at a time. Do not implement all ten strands at once.
- Separate a proposal, a simulated result, an implemented feature and a verified live result.
- Enforce domain and business permissions in application code and storage boundaries, not just prompts.
- Toby coordinates changes through domain tools; broad visibility is not unrestricted write access.
- Keep secrets, real customer records and raw private documents out of committed files and sample data.
- Use synthetic fixtures until real data is deliberately introduced.
- Keep provider SDKs behind adapters. Verify current official documentation before selecting versions or API details.
- Follow the documentation maintenance rules below; do not create decision records merely because work occurred.
- Explain steps plainly. Label commands by where they run; distinguish terminal, editor and provider dashboard.
- These are development guidelines, not additional permission gates. Follow the user's current task authorization.

Current explicit user boundary (7 October 2026): Lisa approved local Tibbi, recipe,
stock and brownie-order workflow foundations. Keep behaviour deterministic and
locally testable; no live Nebius/Nemotron calls or external side effects tonight.
The existing September Toby adapter remains unchanged. The outstanding live full-chain
verification is deferred to Saturday, 10 October 2026. See docs/LOCAL_BROWNIE_FOUNDATIONS.md.

## Documentation maintenance

README.md is the canonical front door. The README describes the system as it exists now, not the system we hope eventually to build. Clearly label intended architecture and proposed work.

After a meaningful implementation milestone has been successfully tested:
1. Update docs/BUILD_JOURNAL.md with what was actually demonstrated, the checks performed, results and limitations.
2. Update docs/STATUS.md if project capability changed.
3. Update README.md only if the high-level description or current capabilities changed. Keep its next-step pointer aligned when the agreed next step changes.
4. Record an architecture decision only when an actual design decision has been made; do not promote an explored idea to a confirmed choice without evidence of that choice.
5. Never describe planned functionality as implemented or an untested change as verified.

For documentation-only maintenance, record the edits and document checks in the journal without claiming a runtime milestone. Leave capability status unchanged when capability has not changed.

Keep detailed information in its designated document and link from README.md. GERA-1-START-HERE.md currently retains the original foundation overview because Lisa asked to read it before changes. Do not maintain it as a competing current summary or change it until she is ready. The proposed eventual role is an access signpost to README.md. When exporting, package the actual workspace.
