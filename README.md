# mta-sts.bada.de

MTA-STS (RFC 8461) policy endpoint for `bada.de`, served via GitHub Pages
at `https://mta-sts.bada.de/.well-known/mta-sts.txt`.

Custom domain is set by the `CNAME` file at the repo root. `.nojekyll`
prevents Jekyll from touching `.well-known/`. GitHub Pages publishes every
committed file of `main`, so everything in this repository is public.

DNS records that must exist for MTA-STS to work:

- `mta-sts.bada.de` CNAME `headfirst-msp.github.io` (serves the policy, TLS automatic)
- `_mta-sts.bada.de` TXT `"v=STSv1; id=..."` (announces the policy; bump `id` on every policy change)
- `_smtp._tls.bada.de` TXT `"v=TLSRPTv1; rua=mailto:..."` (TLS-RPT failure reports)

Policy changes: edit `.well-known/mta-sts.txt`, run `nix flake check -L`,
merge, and bump the `id` in the TXT record. Details, decisions and
verification: `docs/ARCHITECTURE.md`.

Built on the template `project-template`: a reproducible dev shell with the coding agents, the agent
rules, shared skills, the documentation layout and secret handling.

## Getting started

1. Install [Nix](https://nixos.org/download/) with flakes enabled (`experimental-features = nix-command flakes`
   in `nix.conf`) and an SSH key that can read `headfirst-msp/nix-base` on `git.headfirst.cloud`. In the
   repository run `nix develop`. Optional: [nix-direnv](https://github.com/nix-community/nix-direnv) with
   `use flake` in a personal `.envrc` enters the shell on `cd` and caches it.
2. Run `secrets-setup` once: it signs in to OpenBao, sets the keyring as default provider and asks for
   your Forgejo token. Details: `docs/SECRETS.md`.
3. Start an agent as usual with `pi` or `claude`. The Forgejo MCP server gets its token from SecretSpec on its own.

## Checks

`nix flake check -L` runs every git hook on all files, the formatter check and `mta-sts-policy`, which
validates `.well-known/mta-sts.txt` against the policy grammar of RFC 8461
(`scripts/check-mta-sts-policy.py`). Inside the shell the script also runs directly:
`python3 -I scripts/check-mta-sts-policy.py .well-known/mta-sts.txt`.

## What the dev shell provides

The dev shell is the output `devShells.default` of `flake.nix`, and everything is pinned in `flake.lock`.
The tools come from the shared base repository `headfirst-msp/nix-base` (input `nix-base`, imported as
`inputs.nix-base.flakeModules.default`). nix-base follows the `nixpkgs` input of the project
(`nixos-26.05`). The modules and how a project extends or overrides them are described in the README of
`nix-base`.

| Tool | Module in `nix-base` | Notes |
| :--- | :--- | :--- |
| Pi | `agents` (`llm-agents`, package `pi`) | |
| Claude Code | `agents` (`llm-agents`, package `claude-code`) | |
| Forgejo MCP server | `agents` (`lunitrixx`, `mcp.forgejo-mcp`) | Registered for both agents in `.mcp.json`. Lazy tool loading is on |
| OpenBao CLI and scripts | `secrets` | `bao`, `bao-login`, `secrets-setup`, see `docs/SECRETS.md` |
| SecretSpec | `secrets` (from `nixpkgs-unstable` of nix-base) | Provides the secrets declared in `secretspec.toml` |
| Git hooks | `git-hooks` | prek with markdownlint, lychee (offline link check), no em dash in our text, betterleaks (secret scan), no commit on `main` |
| Formatter | `formatter` | `nix fmt` with nixfmt, deadnix and statix, also run as the `treefmt` git hook |
| Changelog fragments | `changelog` | `changelog-add`, `changelog-render`, `changelog-check` and the hooks for `changelog.d/`, see the Changelog section of `AGENTS.md` |

The project adds `git` and `python3` to the shell, the check `mta-sts-policy`, and the markdownlint
excludes for the third-party skills and the PR template, all under `perSystem` in `flake.nix`.

Update all pinned inputs with `nix flake update`, or one of them with `nix flake update <name>`, for
example `nix flake update nix-base`. Commit `flake.lock`.

## Generated files

The shell writes these on entry. They are not committed:

| File | Content |
| :--- | :--- |
| `.mcp.json` | MCP servers for Pi and Claude Code |
| `.pi/settings.json` | Pi project settings |
| `.claude/` | Claude Code settings and the links to the skills |
| `.pre-commit-config.yaml` | Git hook configuration |

Personal settings go to `~/.pi/agent/settings.json` (Pi) or `.claude/settings.local.json`
(Claude Code). Not generated, but also local and never committed: `timesheet.md`, the agents' gitignored time log (see "Time tracking" in `AGENTS.md`).

## workmux

`.workmux.yaml` runs one non-interactive shell start (`nix develop -c true`) in `post_create` of every worktree that `workmux add <branch>`
creates beside the repository (`<repo>__worktrees/<branch>`), before the agent starts. The agent then
finds the generated files, the skill links and the git hooks in place. Agent profiles such as
`coder-qwen` are defined per machine in `~/.config/workmux/config.yaml`, not in the repository.

## Skills

Skills are written once in `.agents/skills/<name>/SKILL.md`. Pi reads that directory itself.
Claude Code reads only `.claude/skills/`, so `nix develop` links every skill directory there on shell
entry with a relative link. The shared skills and their origin are listed in
`.agents/skills/THIRD_PARTY.md`.

## Documentation

`AGENTS.md` is the entry point for agents and lists where knowledge lives. The main pages:

| Page | Content |
| :--- | :--- |
| `docs/ARCHITECTURE.md` | Policy, DNS records, how to change and verify the policy |
| `docs/PLANS.md` | How plans are written; active plans in `docs/exec-plans/active/`, finished ones in `docs/exec-plans/completed/` |
| `docs/SECURITY.md` | Security rules |
| `docs/SECRETS.md` | SecretSpec setup, declared secrets, limits |
| `docs/design-docs/`, `docs/product-specs/` | Design decisions and product behaviour |

The repository is hosted on GitHub. `.forgejo/` holds the template's issue forms and PR template
unchanged; GitHub does not read them.
