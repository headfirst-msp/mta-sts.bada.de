# Tech debt tracker

Known problems that are not fixed yet. One entry per item.

| Area | Problem | Impact | Owner | Status |
| :--- | :--- | :--- | :--- | :--- |
| Policy | `mode` is still `testing` since 2026-10-08, so senders report but do not refuse delivery without valid TLS. | Mail to `bada.de` is not protected against TLS downgrade. | Operator of the `bada.de` zone | Open: check the TLS-RPT reports, then set `mode: enforce` and a new TXT `id` (`docs/ARCHITECTURE.md`, "Changing the policy"). |
