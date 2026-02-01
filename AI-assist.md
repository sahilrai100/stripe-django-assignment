AI Assist Notes

- Tools used: GitHub Copilot (local edits), and ChatGPT for implementation suggestions and quick examples. All code was written/checked by the author and no secrets were pasted into external tools.

Assumptions
- Single-page UX: products shown on main page, Stripe Checkout used to keep the integration small and secure.
- No user accounts required; orders are recorded after the Checkout session completes and webhook events arrive.

Time spent
- Total: ~40 minutes
- Notes: scaffolding, Docker entrypoint, webhook handling, tests, CI.
