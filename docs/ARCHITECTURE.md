# Architecture

The repository is the MTA-STS (RFC 8461) policy host of the mail domain `bada.de`. It has no
application code: GitHub Pages serves the committed files.

## Components

| Part | Where | Role |
| :--- | :--- | :--- |
| `.well-known/mta-sts.txt` | this repository | The policy, served at `https://mta-sts.bada.de/.well-known/mta-sts.txt` |
| `CNAME` | this repository | Custom domain `mta-sts.bada.de` for GitHub Pages |
| `.nojekyll` | this repository | Turns Jekyll off, which would otherwise drop the `.well-known/` directory |
| GitHub Pages | GitHub, source `main`, path `/` | Serves the files over HTTPS with a certificate GitHub issues for the custom domain |
| DNS zone `bada.de` | outside this repository | MX, the policy host and the policy announcement (below) |
| Mail server | Microsoft 365 (Exchange Online) | Receives the mail the policy covers |

Every committed file is public under `https://mta-sts.bada.de/`, docs and the flake included.

## DNS records

| Name | Type | Value | Purpose |
| :--- | :--- | :--- | :--- |
| `bada.de` | MX | `10 bada-de.r-v1.mx.microsoft.` | The host the `mx` lines must match |
| `mta-sts.bada.de` | CNAME | `headfirst-msp.github.io.` | Points the policy host at GitHub Pages |
| `_mta-sts.bada.de` | TXT | `"v=STSv1; id=<revision>"` | Announces the policy; one single record starting with `v=STSv1;` |
| `_smtp._tls.bada.de` | TXT | `"v=TLSRPTv1; rua=mailto:<report mailbox>"` | TLS-RPT: senders report failed TLS deliveries |

Measured on 2026-11-10 with `dig`: all four records exist, the TXT `id` is `20261008`, and the policy
URL answers `HTTP 200` with `content-type: text/plain; charset=utf-8`.

## Policy

Decisions: [0002](design-docs/0002-github-pages-policy-host.md) (hosting) and
[0003](design-docs/0003-policy-mx-patterns-and-mode.md) (`mx` patterns and mode).

- Keys are lowercase and case-sensitive: `version`, `mode`, `mx`, `max_age`. The older STS draft used
  `Version:`; RFC 8461 does not.
- `mode`: `testing` reports failures only, `enforce` refuses delivery without valid TLS, `none` withdraws
  the policy.
- `max_age` is in seconds, at most 31557600. `1209600` is 14 days.
- One `mx:` line per pattern. `*.` replaces exactly the left-most label: `*.example.com` matches
  `mail.example.com`, not `a.b.example.com`. A 4-label host such as `bada-de.r-v1.mx.microsoft` is only
  matched by its exact name.
- `nix flake check -L` runs `scripts/check-mta-sts-policy.py`, which checks the grammar of RFC 8461
  section 3.2 (required keys, values, `mx` syntax). It does not query DNS: compare the `mx` lines with
  `dig +short MX bada.de` by hand.

## Changing the policy

1. Edit `.well-known/mta-sts.txt`, run `nix flake check -L`, merge to `main`.
2. Wait until GitHub Pages serves the new file (`curl -sS https://mta-sts.bada.de/.well-known/mta-sts.txt`).
3. Set a new `id` in the TXT record `_mta-sts.bada.de` (convention: the date, `YYYYMMDD`). Without a new
   `id`, senders keep their cached policy until `max_age` runs out.

## Verification

- `curl -sSI https://mta-sts.bada.de/.well-known/mta-sts.txt`: `HTTP 200` and `content-type: text/plain`.
  Some senders reject other media types.
- Before DNS points at GitHub, fetch through a GitHub Pages address:
  `curl --resolve mta-sts.bada.de:443:<github-pages-ip> https://mta-sts.bada.de/.well-known/mta-sts.txt`.
- Fetches of the project URL `headfirst-msp.github.io/mta-sts.bada.de/` redirect with 301 to the custom
  domain. That is expected.
- An external checker such as `https://support.mta-sts.org` validates DNS, TLS and policy together.

## Setup from scratch

Kept for a rebuild or a second domain:

1. Repository named after the policy host, with the three files above.
2. Enable Pages: `gh api -X POST repos/<org>/<repo>/pages -f source[branch]=main -f source[path]='/'`.
   GitHub reads `CNAME` on the build.
3. Create the CNAME record, wait for the certificate, then the TXT record.
