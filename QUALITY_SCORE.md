# QUALITY_SCORE.md

Last reviewed: 2026-05-03
Owner: Platform / Codex

## Purpose

Quality score is the compact operating dashboard for this repository. Codex updates it when quality gates, architecture rules, test strategy, or risk posture changes.

## Current Score

| Area | Score | Gate | Notes |
| --- | ---: | --- | --- |
| Architecture boundaries | 80 | block on violation | Initial rules and guard exist. |
| Test coverage quality | 55 | warn until app matures | Skeleton tests only. |
| Docs freshness | 85 | block on missing root review dates | Source-of-record docs established. |
| Reliability | 65 | warn | Basic logging and health contract drafted. |
| Security | 65 | block on secret leakage | Baseline policy drafted. |
| Agent operability | 85 | block on harness failure | `scripts/agent-task.sh verify` is primary loop. |

Overall: 72 / 100

## Merge Thresholds

- `>= 80`: normal merge allowed if CI passes.
- `70-79`: merge allowed for small PRs with documented follow-up.
- `60-69`: human review required before merge.
- `< 60`: no feature merge; quality recovery work first.

## Update Triggers

Update this file when:

- a quality gate changes from warn to block or block to warn
- test strategy changes
- architecture rules are added or relaxed
- repeated regressions reveal missing enforcement
- a monthly entropy review completes

## Scoring Rubric

- 90-100: enforced, tested, documented, low ambiguity
- 75-89: mostly enforced, minor manual review remains
- 60-74: documented but partial enforcement
- 40-59: known risk with weak enforcement
- 0-39: unmanaged risk

