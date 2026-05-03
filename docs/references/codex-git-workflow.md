# Codex Git Workflow

Last reviewed: 2026-05-03
Owner: Platform / Codex

## Purpose

This repository does not commit directly on `main`. Codex works in a dedicated worktree branch, merges verified work into `main`, pushes `origin/main`, then removes the worktree and branch.

## Standard Flow

```bash
scripts/agent-task.sh start-report <task-id> "<goal>"
scripts/agent-task.sh worktree-start <task-id>
cd .worktrees/<task-id>

# record the request-intake planning meeting, then create or update
# docs/exec-plans/active/plan-NNNN-<task>.md before task work
scripts/agent-task.sh active-plan

# implement, test, document
scripts/agent-task.sh verify
scripts/agent-task.sh docker-test

# commit and PR from codex/<task-id>
git commit -m "<action>(plan-NNNN): <task>"

# after gates pass:
cd ../..
scripts/agent-task.sh main-merge-push <task-id> <action> "<task>"
scripts/agent-task.sh worktree-clean <task-id>
scripts/agent-task.sh finish-report <task-id> "merged"
```

`verify` is the task-branch command and requires an active plan. `ci` runs the
same non-plan-gate checks for CI or clean `main`, where completed plans normally
leave `docs/exec-plans/active/` empty except for `.gitkeep`.

Default behavior: once work is implemented and required verification passes, Codex must merge and push immediately without waiting for a separate approval. Stop before merge only when the user explicitly asks to pause, when verification fails, or when the operation would be destructive beyond the documented merge/push flow.

Plan gate: Codex must hold a request-intake planning meeting and create or update an active execution plan before task work. If `docs/exec-plans/active/` has no `plan-NNNN-<task>.md` file, stop before implementation, record the meeting output, and create the missing plan from that output. Do not create the plan retroactively at handoff.

## Branch Rules

- Branch format: `codex/<task-id>`.
- Worktree path: `.worktrees/<task-id>`.
- Do not commit on `main`.
- Do not merge without block gates passing.
- Do not wait for separate merge approval after block gates pass unless the user explicitly requested a pause.
- Delete the worktree and branch after merge.

## Commit Message Rules

Commit messages must use:

```text
<action>(plan-NNNN): <task>
```

- `<action>` must be one of `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, or `perf`.
- `plan-NNNN` must match the execution plan or task id.
- `<task>` must be a short imperative summary, for example `docs(plan-0002): update git workflow rules`.

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
3. Run `scripts/agent-task.sh ci` after completing and moving the active plan if a no-active-plan local check is needed.
4. Run `scripts/agent-task.sh main-merge-push <task-id> <action> "<task>"` from the `main` worktree without waiting for extra approval.
5. Remove worktree.
6. Delete local branch.
7. Delete remote branch if it still exists.
8. Send finish report.

## Emergency Exception

Hotfixes still use worktrees. If a production emergency requires compressed review, document the exception in the finish report and create a follow-up debt item.
