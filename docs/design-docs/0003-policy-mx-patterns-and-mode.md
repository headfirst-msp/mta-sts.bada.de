# 0003: Policy mx patterns and rollout mode

- Status: accepted
- Date: 2026-10-08

## Context

The first policy draft listed only `mx: *.mail.protection.outlook.com`. The MX of `bada.de` is
`bada-de.r-v1.mx.microsoft`. RFC 8461 section 4.1 restricts `*` to the whole left-most label, so neither
that pattern nor `*.mx.microsoft` matches the 4-label MX host. In `enforce` mode this would block inbound
mail; in `testing` mode it only produces failure reports.

## Decision

- `mx: bada-de.r-v1.mx.microsoft` (the exact MX host) and `mx: *.mail.protection.outlook.com` as a second
  line, which covers the older Microsoft 365 delivery hosts. Extra `mx` lines are allowed and harmless.
- `mode: testing` for the rollout, `max_age: 1209600` (14 days).
- After a soak period with TLS-RPT reports and no failures, switch to `mode: enforce` and bump the TXT `id`.

## Rejected alternatives

- `mx: *.mx.microsoft`: does not match a 4-label host.
- Starting with `mode: enforce`: a wrong pattern would refuse mail before any report shows the error.

## Consequences

- When Microsoft changes the MX host of the tenant, the policy has to follow before senders cache it.
- The switch to `enforce` is open work: `docs/exec-plans/tech-debt-tracker.md`.
