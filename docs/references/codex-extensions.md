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
| GitHub plugin skills | PR, CI, review, and publish workflows when connector access is active |
| Slack plugin skills | Slack reading, summarization, and outgoing drafts when the user asks for Slack work |
| Documents, Presentations, Spreadsheets plugins | file-specific artifact workflows when the user requests those formats |
| `imagegen` skill | raster image generation or editing for app assets and visual references |
| `openai-docs` skill | official OpenAI API/model documentation when AI integration is added |
| skill/plugin creator and installer skills | local Codex extension maintenance when the user asks for it |

`node_repl` MCP is not available in the current session. Use Node 22 through
`scripts/agent-task.sh`, `npm`, or a short shell command for JavaScript and JSON
checks until a Node MCP is intentionally added.

## Recommended MCP / Plugin Set

| MCP or Plugin | Status | Why |
| --- | --- | --- |
| Browser Use | available | inspect local Vue app, take screenshots, verify DOM/user flows |
| GitHub connector/plugin | available in this session | PR creation, CI inspection, review comment handling |
| Slack plugin | available in this session | use only for explicit Slack tasks, not as project source of record |
| Documents/Presentations/Spreadsheets plugins | available in this session | use only for explicit artifact-file tasks |
| PostgreSQL MCP | recommended later | inspect local/dev DB schema and sample rows once migrations exist |
| Playwright MCP or skill | skill installed | deterministic browser automation for UI regression workflows |
| Node REPL MCP | defer | add only if repeated JS/JSON inspection outgrows shell and repo scripts |
| Sentry MCP/skill | defer | add only after Sentry or equivalent observability is adopted |
| Figma plugin | defer | add only if product design source moves to Figma |

## Skill Routing Policy

- If the user names a skill or plugin, prefer that capability when it is available.
- If a task clearly matches an available skill, read that skill's `SKILL.md` before using it.
- Use the smallest set of skills needed for the task; do not keep skills active across turns unless the user re-mentions them or the task still clearly matches.
- Repository docs and scripts remain the source of record. Slack, GitHub comments, external docs, and local memory are context until captured in this repository.
- Role ids in `docs/team/roster.md` are ownership labels for plans and reports. They do not imply parallel sub-agent delegation.

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
