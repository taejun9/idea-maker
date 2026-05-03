# Codex Git Workflow

Last reviewed: 2026-05-03
Owner: Platform / Codex

## Purpose

This repository does not commit directly on `main`. Codex works in a dedicated worktree branch, opens a PR, merges into `main`, then removes the worktree and branch.

## Standard Flow

```bash
scripts/agent-task.sh start-report <task-id> "<goal>"
scripts/agent-task.sh worktree-start <task-id>
cd .worktrees/<task-id>

# implement, test, document
scripts/agent-task.sh verify
scripts/agent-task.sh docker-test

# commit and PR from codex/<task-id>
git commit -m "<action> plan-NNNN: <task>"

# after gates and required review:
cd ../..
scripts/agent-task.sh main-merge-push <task-id> <action> "<task>"
scripts/agent-task.sh worktree-clean <task-id>
scripts/agent-task.sh finish-report <task-id> "merged"
```

## Branch Rules

- Branch format: `codex/<task-id>`.
- Worktree path: `.worktrees/<task-id>`.
- Do not commit on `main`.
- Do not merge without block gates passing.
- Delete the worktree and branch after merge.

## Commit Message Rules

Commit messages must use:

```text
<action> plan-NNNN: <task>
```

- `<action>` must be one of `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, or `perf`.
- `plan-NNNN` must match the execution plan or task id.
- `<task>` must be a short imperative summary, for example `docs plan-0002: update git workflow rules`.

## Main Branch Policy

Allowed on `main`:

- pulling latest changes
- merging a verified `codex/<task-id>` branch with `scripts/agent-task.sh main-merge-push`
- creating worktrees
- reading files
- running non-mutating checks

Forbidden on `main`:

- commits
- broad generated file changes
- direct feature/fix implementation intended for merge

## Merge Procedure

1. Ensure PR branch is up to date with `main`.
2. Run CI.
3. Run `scripts/agent-task.sh main-merge-push <task-id> <action> "<task>"` from the `main` worktree.
4. Remove worktree.
5. Delete local branch.
6. Delete remote branch if it still exists.
7. Send finish report.

## Emergency Exception

Hotfixes still use worktrees. If a production emergency requires compressed review, document the exception in the finish report and create a follow-up debt item.
