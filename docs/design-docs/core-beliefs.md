# Core Beliefs

Last reviewed: 2026-05-03
Owner: Product / Platform / Codex

## Product Beliefs

- Users come with vague ideas and need a concrete report, not a blank canvas.
- A useful report combines idea clarification, target users, advantages, disadvantages, domestic competitors, overseas competitors, and adjacent startup references.
- Recommendations must identify source, retrieval date, and confidence because startup directories change quickly.
- Domestic and overseas competitor analysis must be separated; the user needs market context, not a single generic list.

## Engineering Beliefs

- Codex works best when boundaries are explicit, files are small, and validation is mechanical.
- Repository docs are the system of record.
- `AGENTS.md` is a map; it should not become a long manual.
- Every broad task needs an execution plan with rollback and verification.
- Every warning that blocks future quality should become tracked debt or an enforced rule.

## Agent-First Beliefs

- If Codex cannot inspect it locally, the system should not depend on it.
- The happy path and failure path must both be scriptable.
- UI state, backend logs, and test output should be readable without tribal knowledge.
- Repeated human review comments should graduate into lint rules, templates, or docs.

