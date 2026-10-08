# mta-sts.bada.de

MTA-STS (RFC 8461) policy endpoint for `bada.de`, served via GitHub Pages
at `https://mta-sts.bada.de/.well-known/mta-sts.txt`.

Custom domain is set by the `CNAME` file at the repo root. `.nojekyll`
prevents Jekyll from touching `.well-known/`.

DNS records that must exist for MTA-STS to work:

- `mta-sts.bada.de` CNAME `headfirst-msp.github.io` (serves the policy, TLS automatic)
- `_mta-sts.bada.de` TXT `"v=STSv1; id=..."` (announces the policy; bump `id` on every policy change)

Policy changes: edit `.well-known/mta-sts.txt`, commit, and bump the `id`
in the TXT record.
