#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

cmd="${1:-help}"
PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  else
    echo "No python or python3 executable found" >&2
    exit 127
  fi
fi

run_python_check() {
  "$PYTHON_BIN" "$1"
}

run_doctor_checks() {
  run_python_check tools/agent_doctor.py
  run_python_check tools/structure_guard.py
}

run_layer_checks() {
  "$0" docs
  "$0" architecture
  "$0" exec-plans
  "$0" quality
  if [ -f pyproject.toml ]; then "$0" backend; fi
  "$0" frontend
}

require_active_plan() {
  local active_plans
  active_plans="$(find docs/exec-plans/active -maxdepth 1 -type f -name 'plan-[0-9][0-9][0-9][0-9]-*.md' -print -quit 2>/dev/null || true)"
  if [ -z "$active_plans" ]; then
    echo "No active execution plan found. Create docs/exec-plans/active/plan-NNNN-<task>.md before task work." >&2
    exit 2
  fi
}

case "$cmd" in
  start-report)
    task_id="${2:-[TASK_ID]}"
    goal="${3:-[GOAL]}"
    cat <<EOF
Task start report
- team: 개미군단 (ant-legion)
- task: $task_id
- goal: $goal
- branch: codex/$task_id
- worktree: .worktrees/$task_id
- roles: [ROLE_IDS]
- verification: scripts/agent-task.sh verify; scripts/agent-task.sh docker-test when runtime changed
EOF
    ;;
  finish-report)
    task_id="${2:-[TASK_ID]}"
    status="${3:-[STATUS]}"
    cat <<EOF
Task finish report
- team: 개미군단 (ant-legion)
- task: $task_id
- status: $status
- required summary: changed files, commands run, pass/fail, docs updated, remaining risks
EOF
    ;;
  worktree-start)
    task_id="${2:?task id required, e.g. plan-0001-idea-report-mvp}"
    branch="codex/$task_id"
    worktree=".worktrees/$task_id"
    git fetch origin main || true
    git worktree add -b "$branch" "$worktree" main
    echo "Created worktree $worktree on branch $branch"
    ;;
  worktree-clean)
    task_id="${2:?task id required, e.g. plan-0001-idea-report-mvp}"
    branch="codex/$task_id"
    worktree=".worktrees/$task_id"
    git worktree remove "$worktree"
    git branch -d "$branch"
    echo "Removed worktree $worktree and branch $branch"
    ;;
  main-merge-push)
    task_id="${2:?task id required, e.g. plan-0001-idea-report-mvp}"
    action="${3:-chore}"
    if [[ ! "$task_id" =~ ^(plan-[0-9]{4})-(.+)$ ]]; then
      echo "task id must use plan-NNNN-<task>, got: $task_id" >&2
      exit 2
    fi
    plan_id="${BASH_REMATCH[1]}"
    task_slug="${BASH_REMATCH[2]}"
    if [[ ! "$action" =~ ^(feat|fix|docs|test|refactor|chore|ci|perf)$ ]]; then
      echo "action must be one of: feat, fix, docs, test, refactor, chore, ci, perf" >&2
      exit 2
    fi
    if [ "$#" -ge 4 ]; then
      shift 3
      task_summary="$*"
    else
      task_summary="${task_slug//-/ }"
    fi
    branch="codex/$task_id"
    current_branch="$(git branch --show-current)"
    if [ "$current_branch" != "main" ]; then
      echo "main-merge-push must run from the main worktree; current branch: $current_branch" >&2
      exit 2
    fi
    if ! git diff --quiet || ! git diff --cached --quiet; then
      echo "main-merge-push requires a clean main worktree" >&2
      exit 2
    fi
    if ! git show-ref --verify --quiet "refs/heads/$branch"; then
      echo "Branch not found: $branch" >&2
      exit 2
    fi
    git fetch origin main
    git merge --ff-only origin/main
    git merge --no-ff "$branch" -m "$action($plan_id): $task_summary"
    git push origin main
    echo "Merged $branch into main and pushed origin/main"
    ;;
  active-plan)
    require_active_plan
    echo "active_plan: ok"
    ;;
  doctor)
    require_active_plan
    run_doctor_checks
    ;;
  docs)
    run_python_check tools/docs_freshness.py
    run_python_check tools/link_check.py
    ;;
  architecture)
    run_python_check tools/architecture_scan.py
    ;;
  exec-plans)
    run_python_check tools/exec_plan_guard.py
    ;;
  quality)
    run_python_check tools/quality_score.py
    ;;
  backend)
    if ! "$PYTHON_BIN" -c "import pytest, ruff" >/dev/null 2>&1; then
      echo "backend: skipped; use scripts/agent-task.sh docker-test or install dev dependencies"
    elif [ -f pyproject.toml ]; then
      "$PYTHON_BIN" -m pytest services/api/tests tests
      "$PYTHON_BIN" -m ruff check services/api tests tools
    else
      echo "backend: skipped; pyproject.toml not found"
    fi
    ;;
  frontend)
    if [ ! -x node_modules/.bin/vue-tsc ]; then
      echo "frontend: skipped; use scripts/agent-task.sh docker-test or run npm install"
    elif [ -f apps/web/package.json ]; then
      npm run --workspace apps/web build
      npm run --workspace apps/web test
    else
      echo "frontend: skipped; apps/web/package.json not found"
    fi
    ;;
  verify)
    "$0" active-plan
    run_doctor_checks
    run_layer_checks
    ;;
  ci)
    run_doctor_checks
    run_layer_checks
    ;;
  docker-up)
    docker compose up -d --build
    ;;
  docker-down)
    docker compose down
    ;;
  docker-test)
    docker compose run --rm api python -m pytest services/api/tests tests
    docker compose run --rm api python -m ruff check services/api tests tools
    docker compose run --rm --no-deps web npm install
    docker compose run --rm --no-deps web npm run --workspace apps/web build
    docker compose run --rm --no-deps web npm run --workspace apps/web test
    ;;
  help|*)
    cat <<'EOF'
Usage: scripts/agent-task.sh <command>

Commands:
  doctor        Show local environment and required harness files
  start-report  Print a task start report template
  finish-report Print a task finish report template
  worktree-start Create .worktrees/<task-id> on codex/<task-id>
  worktree-clean Remove .worktrees/<task-id> and delete codex/<task-id>
  main-merge-push Merge codex/<task-id> into main and push origin/main
  active-plan  Require at least one active execution plan
  docs          Check docs freshness and local markdown links
  architecture  Run architecture boundary scan
  exec-plans   Validate execution plan placement and required sections
  quality       Check docs/quality/quality-score.md
  backend       Run backend lint/tests
  frontend      Run frontend build/tests
  verify        Run the task-branch Codex verification loop with active-plan gate
  ci            Run the main/CI-safe verification loop without active-plan gate
  docker-up     Start local Docker runtime
  docker-down   Stop local Docker runtime
  docker-test   Run Docker-based backend/frontend tests
EOF
    ;;
esac
