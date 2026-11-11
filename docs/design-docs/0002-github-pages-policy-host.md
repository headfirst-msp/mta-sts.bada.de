# 0002: GitHub Pages hosts the MTA-STS policy

- Status: accepted
- Date: 2026-10-08

## Context

RFC 8461 requires the policy at `https://mta-sts.<domain>/.well-known/mta-sts.txt` with a valid public
certificate and the media type `text/plain`. The mail of `bada.de` runs on Microsoft 365, which does not
host MTA-STS policies.

## Decision

A public GitHub repository named after the policy host serves the policy through GitHub Pages from `main`,
repository root. `CNAME` sets the custom domain, `.nojekyll` keeps `.well-known/` published, and GitHub
issues the certificate. The DNS record `mta-sts.bada.de` is a CNAME to `headfirst-msp.github.io`.

## Rejected alternatives

- A web server of our own: needs hosting, certificate renewal and monitoring for one static file.

## Consequences

- No server to run; certificate renewal is GitHub's.
- Every committed file is public under the policy host.
- A policy change is live once Pages has rebuilt `main`; the DNS TXT `id` still has to be changed by hand.
