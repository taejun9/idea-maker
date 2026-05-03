# Codex Skills and MCP Extensions

Last reviewed: 2026-05-03
Owner: Platform / Codex

## Purpose

This file records the skills and MCP/plugin capabilities recommended for 개미군단 (`ant-legion`). It separates what is installed now from what should be added only when the project needs it.

## Installed Skills

Installed into `$CODEX_HOME/skills` on 2026-05-03:

| Skill | Why It Is Needed | Usage Trigger |
| --- | --- | --- |
| `playwright` | browser-level UI verification for Vue workflows | frontend behavior or layout changes |
| `yeet` | publish local branch work to GitHub PRs | ready to commit, push, and open PR |
| `gh-fix-ci` | inspect and fix failing GitHub Actions checks | CI failure on PR |
| `gh-address-comments` | resolve actionable PR review comments | review feedback arrives |
| `security-best-practices` | baseline secure implementation review | auth, data, external source, dependency work |
| `security-threat-model` | structured threat modeling | new user data, source collection, sharing/export, deployment |

Codex must be restarted for newly installed skills to appear in the active skill list.

## Already Available In This Session

| Capability | Use |
| --- | --- |
| `browser-use` plugin | in-app browser checks for localhost UI |
| `node_repl` MCP | quick JavaScript/JSON inspection and generated artifact checks |
| GitHub plugin skills | PR, CI, and review workflows when connector access is active |
| `openai-docs` skill | official OpenAI API/model documentation when AI integration is added |

## Recommended MCP / Plugin Set

| MCP or Plugin | Status | Why |
| --- | --- | --- |
| Browser Use | available | inspect local Vue app, take screenshots, verify DOM/user flows |
| Node REPL MCP | available | run small JS checks and parse JSON/config without adding repo scripts |
| GitHub connector/plugin | available in this session | PR creation, CI inspection, review comment handling |
| PostgreSQL MCP | recommended later | inspect local/dev DB schema and sample rows once migrations exist |
| Playwright MCP or skill | skill installed | deterministic browser automation for UI regression workflows |
| Sentry MCP/skill | defer | add only after Sentry or equivalent observability is adopted |
| Figma plugin | defer | add only if product design source moves to Figma |

## Installation Policy

- Install a skill only when it maps to a repeated workflow.
- Do not install deployment skills before the deployment target is chosen.
- Prefer repository docs and scripts over hidden personal workflows.
- Record every installed skill here with date, reason, and usage trigger.
- If an MCP server requires secrets, document environment variables in `.env.example` and security implications in `docs/operations/security.md`.

## Next Candidates

Add later when the trigger is real:

| Candidate | Trigger |
| --- | --- |
| `sentry` | production error monitoring is adopted |
| `vercel-deploy`, `render-deploy`, or `cloudflare-deploy` | deployment platform is selected |
| `figma-implement-design` | UI work starts from Figma files |

