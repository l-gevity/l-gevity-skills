#!/usr/bin/env bash
# Functional tests for .install/install-*.sh.
#
# Hermetic by construction: builds an archive from the working tree and points
# the installers at it with L_GEVITY_SKILLS_ARCHIVE, so the code under test is
# the checkout's, not a published tag, and the run needs no network.
#
# Static structure (family parity, agent profiles, count source) is checked by
# scripts/validate-skills.py. This file checks behavior.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# The installers add the Unstoppable adapter when the session shows the app.
# Clear its variables, so every run here starts outside it wherever the suite
# itself is run.
for name in $(env | grep -oE '^(UNSTOPPABLE_CODE|CANOPY)_[A-Za-z0-9_]*' || true); do
  unset "$name"
done

fails=0
checks=0

check() {
  checks=$((checks + 1))
  if [ "$2" = "$3" ]; then
    echo "  PASS $1"
  else
    echo "  FAIL $1: expected [$3] got [$2]"
    fails=$((fails + 1))
  fi
}

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d' ' -f1
  else
    shasum -a 256 "$1" | cut -d' ' -f1
  fi
}

tree_hashes() {
  ( cd "$1" && find . -type f ! -name 'l-gevity-skills.lock.json' | LC_ALL=C sort |
      while IFS= read -r f; do printf '%s  %s\n' "$(sha256_of "$f")" "$f"; done )
}

ZERO64="0000000000000000000000000000000000000000000000000000000000000000"

# Record a path in the lock's file map so the next run treats it as previously
# installed. Text-only, so the suite needs no interpreter beyond the shell.
lock_inject() {
  awk -v entry="        \"$2\": \"$ZERO64\"," '
    { print }
    /^    "files": \{$/ { print entry }
  ' "$1" > "$1.tmp" && mv "$1.tmp" "$1"
}

# The installers expect one top-level l-gevity-skills-* directory in the archive.
STAGE="$WORK/l-gevity-skills-test"
mkdir -p "$STAGE"
cp -R "$REPO_ROOT/.claude" "$STAGE/"
cp -R "$REPO_ROOT/.agents" "$STAGE/"
cp "$REPO_ROOT/CLAUDE.md" "$STAGE/"
ARCHIVE="$WORK/skills.tar.gz"
tar -czf "$ARCHIVE" -C "$WORK" "l-gevity-skills-test"
export L_GEVITY_SKILLS_ARCHIVE="$ARCHIVE"

SRC_SKILLS="$REPO_ROOT/.claude/skills"
EXPECT_SKILLS="$(find "$SRC_SKILLS" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
EXPECT_FILES="$(cd "$SRC_SKILLS" && find . -type f ! -name '*.pyc' ! -name '*.pyo' | wc -l | tr -d ' ')"
echo "Source tree: $EXPECT_SKILLS skills, $EXPECT_FILES files"
echo

primary_dir_for() {
  case "$1" in
    claude) echo ".claude/skills" ;;
    *) echo ".agents/skills" ;;
  esac
}

memfile_for() {
  case "$1" in
    claude) echo "CLAUDE.md" ;;
    codex) echo "AGENTS.md" ;;
    gemini) echo "GEMINI.md" ;;
    grok) echo "GROK.md" ;;
  esac
}

adapter_runtime_for() {
  case "$1" in
    claude) echo "claude-code" ;;
    codex) echo "codex" ;;
  esac
}

adapter_file_for() {
  case "$1" in
    claude) echo ".claude/agents/alchemy-analyst.md" ;;
    codex) echo ".codex/agents/alchemy-analyst.toml" ;;
  esac
}

# The adapter step needs Python 3, found by the probe the installers use. A
# host without it still runs every check: the installers must then say so.
PYTHON=""
for candidate in python3 python; do
  if [ -z "$PYTHON" ] && "$candidate" -c 'import sys; sys.exit(sys.version_info[0] != 3)' >/dev/null 2>&1; then
    PYTHON="$candidate"
  fi
done
echo "Python 3: ${PYTHON:-not found}"
echo

# --- Every installer lands in its own agent's tree and reports the source ---
for agent in claude codex gemini grok; do
  echo "== $agent: installs into its own tree =="
  primary="$(primary_dir_for "$agent")"
  memfile="$(memfile_for "$agent")"
  other=".claude/skills"
  [ "$primary" = ".claude/skills" ] && other=".agents/skills"

  T="$WORK/consumer-$agent"
  mkdir -p "$T"
  ( cd "$T" && bash "$REPO_ROOT/.install/install-$agent.sh" ) > "$WORK/$agent.log" 2>&1
  check "exit status" "$?" "0"
  check "skills in $primary" \
    "$([ -f "$T/$primary/alchemy/SKILL.md" ] && echo yes || echo no)" "yes"
  check "nothing written to $other" \
    "$([ -d "$T/$other" ] && echo yes || echo no)" "no"
  check "created $memfile" "$([ -f "$T/$memfile" ] && echo yes || echo no)" "yes"
  check "reported skill count" \
    "$(grep -oE 'Installed [0-9]+ skills' "$WORK/$agent.log" | grep -oE '[0-9]+')" \
    "$EXPECT_SKILLS"
  check "reported file count" \
    "$(grep -oE '\([0-9]+ files\)' "$WORK/$agent.log" | grep -oE '[0-9]+')" \
    "$EXPECT_FILES"

  LOCK="$T/$primary/l-gevity-skills.lock.json"
  check "lock version 2" \
    "$(grep -oE '"version": [0-9]+' "$LOCK" | grep -oE '[0-9]+')" "2"
  check "lock names the agent" \
    "$(grep -oE '"agent": "[a-z]+"' "$LOCK" | cut -d'"' -f4)" "$agent"
  check "one hash per installed file" \
    "$(grep -cE '"[^"]+": "[0-9a-f]{64}"' "$LOCK")" "$EXPECT_FILES"

  runtime="$(adapter_runtime_for "$agent")"
  if [ -z "$runtime" ]; then
    check "says no adapter ships for $agent" \
      "$(grep -c "^Agent-team adapters: none shipped for $agent" "$WORK/$agent.log")" "1"
    check "no workspace profile written" \
      "$([ -e "$T/alchemy-workspace.json" ] && echo yes || echo no)" "no"
  elif [ -n "$PYTHON" ]; then
    check "reports the $runtime adapters" \
      "$(grep -cx "Agent-team adapters: $runtime" "$WORK/$agent.log")" "1"
    check "agent definition rendered" \
      "$([ -f "$T/$(adapter_file_for "$agent")" ] && echo yes || echo no)" "yes"
    check "workspace profile written" \
      "$([ -f "$T/alchemy-workspace.json" ] && echo yes || echo no)" "yes"
    check "no Unstoppable files outside Unstoppable" \
      "$([ -e "$T/.unstoppable-code" ] && echo yes || echo no)" "no"
  else
    check "reports the adapters as not installed" \
      "$(grep -c '^Agent-team adapters: not installed (Python 3 not found)' "$WORK/$agent.log")" "1"
  fi
  echo
done

# --- A recorded hash matches the bytes actually installed ---
echo "== recorded hashes describe the installed bytes =="
T="$WORK/consumer-claude"
LOCK="$T/.claude/skills/l-gevity-skills.lock.json"
mismatch=0
while IFS= read -r entry; do
  rel="$(printf '%s' "$entry" | cut -d'"' -f2)"
  want="$(printf '%s' "$entry" | grep -oE '[0-9a-f]{64}')"
  got="$(sha256_of "$T/.claude/skills/$rel")"
  [ "$got" = "$want" ] || mismatch=$((mismatch + 1))
done < <(grep -oE '"[^"]+": "[0-9a-f]{64}"' "$LOCK")
check "hash mismatches across every file" "$mismatch" "0"
echo

# --- An existing instruction file of any name is honored ---
echo "== an existing AGENTS.md is honored by the Claude installer =="
T="$WORK/consumer-agents-md"
mkdir -p "$T"
printf 'project instructions\n' > "$T/AGENTS.md"
( cd "$T" && bash "$REPO_ROOT/.install/install-claude.sh" ) > "$WORK/agents-md.log" 2>&1
check "existing file untouched" "$(cat "$T/AGENTS.md")" "project instructions"
check "upstream copy sidecarred" \
  "$([ -f "$T/AGENTS.md.l-gevity" ] && echo yes || echo no)" "yes"
check "no second instruction file invented" \
  "$([ -f "$T/CLAUDE.md" ] && echo yes || echo no)" "no"
echo

# --- An instruction file that differs only in line endings is current ---
echo "== a CRLF copy of the current CLAUDE.md gets no sidecar =="
T="$WORK/consumer-crlf-claude-md"
mkdir -p "$T"
awk '{ printf "%s\r\n", $0 }' "$STAGE/CLAUDE.md" > "$T/CLAUDE.md"
printf 'stale sidecar\n' > "$T/CLAUDE.md.l-gevity"
( cd "$T" && bash "$REPO_ROOT/.install/install-claude.sh" ) > "$WORK/crlf-claude-md.log" 2>&1
check "no sidecar for a line-ending-only difference" \
  "$([ -f "$T/CLAUDE.md.l-gevity" ] && echo yes || echo no)" "no"
check "reported as current" "$(grep -c 'CLAUDE.md (already current)' "$WORK/crlf-claude-md.log")" "1"
echo

# --- A consumer keeping both trees gets both, identically ---
echo "== a dual-tree consumer keeps its mirror =="
T="$WORK/consumer-both"
mkdir -p "$T/.claude/skills" "$T/.agents/skills"
( cd "$T" && bash "$REPO_ROOT/.install/install-claude.sh" ) > "$WORK/both.log" 2>&1
check "primary tree filled" \
  "$([ -f "$T/.claude/skills/alchemy/SKILL.md" ] && echo yes || echo no)" "yes"
check "mirror tree filled" \
  "$([ -f "$T/.agents/skills/alchemy/SKILL.md" ] && echo yes || echo no)" "yes"
check "trees byte-identical" \
  "$(diff -r "$T/.claude/skills" "$T/.agents/skills" >/dev/null 2>&1 && echo identical || echo differs)" \
  "identical"
echo

# --- Re-running changes nothing ---
echo "== the installer is idempotent =="
BEFORE="$WORK/before.txt"
AFTER="$WORK/after.txt"
tree_hashes "$T/.claude/skills" > "$BEFORE"
( cd "$T" && bash "$REPO_ROOT/.install/install-claude.sh" ) > "$WORK/idem.log" 2>&1
tree_hashes "$T/.claude/skills" > "$AFTER"
check "second run leaves the tree unchanged" \
  "$(diff "$BEFORE" "$AFTER" >/dev/null && echo unchanged || echo changed)" "unchanged"
check "second run removes nothing" \
  "$(grep -c 'Removed' "$WORK/idem.log" || true)" "0"
check "second run renders no adapter file again" \
  "$(grep -cE ': (created|kept)' "$WORK/idem.log" || true)" "0"
echo

# --- The adapter step never overwrites what the project already has ---
echo "== an existing settings file is kept, the rendered one written beside it =="
T="$WORK/consumer-settings"
mkdir -p "$T/.claude"
printf '{"mine": true}\n' > "$T/.claude/settings.json"
( cd "$T" && bash "$REPO_ROOT/.install/install-claude.sh" ) > "$WORK/settings.log" 2>&1
check "existing settings untouched" "$(cat "$T/.claude/settings.json")" '{"mine": true}'
if [ -n "$PYTHON" ]; then
  check "rendered settings sidecarred" \
    "$([ -f "$T/.claude/settings.json.l-gevity" ] && echo yes || echo no)" "yes"
fi
echo

# --- Unstoppable Code gets its pipeline beside the harness's adapter ---
if [ -n "$PYTHON" ]; then
  PIPELINE=".unstoppable-code/pipelines/alchemy-multi-agent.yaml"

  echo "== a project with an .unstoppable-code directory gets the pipeline =="
  T="$WORK/consumer-unstoppable-dir"
  mkdir -p "$T/.unstoppable-code"
  ( cd "$T" && bash "$REPO_ROOT/.install/install-codex.sh" ) > "$WORK/unstoppable-dir.log" 2>&1
  check "reports both adapters" \
    "$(grep -cx 'Agent-team adapters: codex unstoppable' "$WORK/unstoppable-dir.log")" "1"
  check "pipeline installed" "$([ -f "$T/$PIPELINE" ] && echo yes || echo no)" "yes"
  check "harness agent rendered" \
    "$([ -f "$T/.codex/agents/alchemy-analyst.toml" ] && echo yes || echo no)" "yes"
  echo

  echo "== a session started by Unstoppable Code gets the pipeline =="
  T="$WORK/consumer-unstoppable-env"
  mkdir -p "$T"
  ( cd "$T" && UNSTOPPABLE_CODE_SESSION=1 bash "$REPO_ROOT/.install/install-claude.sh" ) \
    > "$WORK/unstoppable-env.log" 2>&1
  check "reports both adapters" \
    "$(grep -cx 'Agent-team adapters: claude-code unstoppable' "$WORK/unstoppable-env.log")" "1"
  check "pipeline installed" "$([ -f "$T/$PIPELINE" ] && echo yes || echo no)" "yes"
  echo
fi

MANUAL="python .claude/skills/alchemy-orchestrate/scripts/init_workspace.py --runtime claude-code"

# --- A profile the adapter installer refuses is reported; the skills stay ---
if [ -n "$PYTHON" ]; then
  echo "== a refused workspace profile does not fail the install =="
  T="$WORK/consumer-bad-profile"
  mkdir -p "$T"
  printf '{"schema": "alchemy-workspace/1", "execution": {"max_parallel_agents": 0}}\n' \
    > "$T/alchemy-workspace.json"
  ( cd "$T" && bash "$REPO_ROOT/.install/install-claude.sh" ) > "$WORK/bad-profile.log" 2>&1
  check "exit status" "$?" "0"
  check "failure reported with the command to rerun" \
    "$(grep -cxF "Agent-team adapters: not installed (init_workspace.py failed, see above); fix and run: $MANUAL" "$WORK/bad-profile.log")" "1"
  check "no agent definition rendered" \
    "$([ -e "$T/.claude/agents" ] && echo yes || echo no)" "no"
  check "skills installed" \
    "$([ -f "$T/.claude/skills/alchemy/SKILL.md" ] && echo yes || echo no)" "yes"
  echo
fi

# --- Without Python 3 the skills install and the gap is named ---
echo "== a host without Python 3 still installs the skills =="
NOPY="$WORK/no-python"
mkdir -p "$NOPY"
for name in python3 python; do
  printf '#!/bin/sh\nexit 1\n' > "$NOPY/$name"
  chmod +x "$NOPY/$name"
done
T="$WORK/consumer-no-python"
mkdir -p "$T"
( cd "$T" && PATH="$NOPY:$PATH" bash "$REPO_ROOT/.install/install-claude.sh" ) > "$WORK/no-python.log" 2>&1
check "exit status" "$?" "0"
check "gap reported with the command to run" \
  "$(grep -cxF "Agent-team adapters: not installed (Python 3 not found); run: $MANUAL" "$WORK/no-python.log")" "1"
check "no agent definition rendered" \
  "$([ -e "$T/.claude/agents" ] && echo yes || echo no)" "no"
check "skills installed" \
  "$([ -f "$T/.claude/skills/alchemy/SKILL.md" ] && echo yes || echo no)" "yes"
echo

# --- A file upstream no longer ships is removed and reported ---
echo "== a dropped file is pruned on the next run =="
STALE="$T/.claude/skills/alchemy/RETIRED.md"
printf 'gone upstream\n' > "$STALE"
lock_inject "$T/.claude/skills/l-gevity-skills.lock.json" 'alchemy/RETIRED.md'
( cd "$T" && bash "$REPO_ROOT/.install/install-claude.sh" ) > "$WORK/prune.log" 2>&1
check "stale file removed" "$([ -f "$STALE" ] && echo present || echo gone)" "gone"
check "removal reported" \
  "$(grep -c 'Removed (dropped upstream): .claude/skills/alchemy/RETIRED.md' "$WORK/prune.log")" "1"
check "sibling files survive" \
  "$([ -f "$T/.claude/skills/alchemy/SKILL.md" ] && echo yes || echo no)" "yes"
echo

# --- A lock naming a path outside the tree must not delete anything ---
echo "== path traversal in the lock is refused =="
printf 'do not delete me\n' > "$T/CANARY.md"
lock_inject "$T/.claude/skills/l-gevity-skills.lock.json" '../../CANARY.md'
( cd "$T" && bash "$REPO_ROOT/.install/install-claude.sh" ) > "$WORK/traversal.log" 2>&1
check "file outside the tree survives" \
  "$([ -f "$T/CANARY.md" ] && echo present || echo deleted)" "present"
check "refusal reported" \
  "$(grep -c 'Refused to remove unsafe path from lock: ../../CANARY.md' "$WORK/traversal.log")" "1"
check "install still succeeds" \
  "$(grep -c 'Installed .* skills' "$WORK/traversal.log")" "1"

echo
# --- grep -q exits on its first match; under pipefail the writer's SIGPIPE must
# not read as "dropped upstream". Past the pipe buffer this fails on every OS.
echo "== a long file list survives a second run =="
LONG="$WORK/long"
mkdir -p "$LONG"
cp -R "$STAGE" "$LONG/l-gevity-skills-test"
LONG_DIR="$LONG/l-gevity-skills-test/.claude/skills/zz-long"
LONG_NAME="$(printf 'x%.0s' $(seq 1 130))"
mkdir -p "$LONG_DIR"
for n in $(seq 1 500); do
  : > "$LONG_DIR/$n-$LONG_NAME.md"
done
tar -czf "$LONG/skills.tar.gz" -C "$LONG" "l-gevity-skills-test"
LT="$WORK/long-target"
mkdir -p "$LT"
( cd "$LT" && L_GEVITY_SKILLS_ARCHIVE="$LONG/skills.tar.gz" bash "$REPO_ROOT/.install/install-claude.sh" ) > /dev/null 2>&1
( cd "$LT" && L_GEVITY_SKILLS_ARCHIVE="$LONG/skills.tar.gz" bash "$REPO_ROOT/.install/install-claude.sh" ) > "$WORK/long.log" 2>&1
check "second run removes nothing" "$(grep -c 'Removed' "$WORK/long.log" || true)" "0"
check "every file is still there" \
  "$(find "$LT/.claude/skills/zz-long" -type f | wc -l | tr -d ' ')" "500"


# --- The uninstaller removes an unedited install and nothing else ---
uninstall_in() {
  ( cd "$1" && shift && "$@" bash "$REPO_ROOT/.install/uninstall.sh" )
}

echo
echo "== an unedited install is removed completely =="
T="$WORK/uninstall-clean"
mkdir -p "$T"
( cd "$T" && bash "$REPO_ROOT/.install/install-claude.sh" ) > /dev/null 2>&1
uninstall_in "$T" env > "$WORK/uninstall-clean.log" 2>&1
check "exit status" "$?" "0"
check "nothing left in the project" "$(find "$T" -mindepth 1 | wc -l | tr -d ' ')" "0"
check "instruction file reported removed" \
  "$(grep -cx 'Instruction file: removed CLAUDE.md' "$WORK/uninstall-clean.log")" "1"
check "every installed file reported removed" \
  "$(grep -oE '^Removed [0-9]+ file' "$WORK/uninstall-clean.log" | grep -oE '[0-9]+')" "$EXPECT_FILES"
uninstall_in "$T" env > "$WORK/uninstall-again.log" 2>&1
check "second run exits 0" "$?" "0"
check "second run finds nothing" "$(grep -c '^Nothing to uninstall' "$WORK/uninstall-again.log")" "1"

echo
echo "== edited files and the project's own instruction file are kept =="
T="$WORK/uninstall-edited"
mkdir -p "$T"
printf 'project instructions\n' > "$T/AGENTS.md"
( cd "$T" && bash "$REPO_ROOT/.install/install-claude.sh" ) > /dev/null 2>&1
check "lock names the sidecar it wrote" \
  "$(tr -d '\r\n' < "$T/.claude/skills/l-gevity-skills.lock.json" | grep -oE '"instructionFile" *: *\{ *"path": "[^"]*"' | grep -oE '[^"]+"$' | tr -d '"')" \
  "AGENTS.md.l-gevity"
printf 'local note\n' >> "$T/.claude/skills/alchemy/SKILL.md"
uninstall_in "$T" env > "$WORK/uninstall-edited.log" 2>&1
check "exit status" "$?" "0"
check "project instruction file untouched" "$(cat "$T/AGENTS.md")" "project instructions"
check "installed sidecar removed" "$([ -e "$T/AGENTS.md.l-gevity" ] && echo yes || echo no)" "no"
check "edited skill file kept" \
  "$([ -f "$T/.claude/skills/alchemy/SKILL.md" ] && echo yes || echo no)" "yes"
check "edited skill file reported" \
  "$(grep -c 'Kept (edited since install): .claude/skills/alchemy/SKILL.md' "$WORK/uninstall-edited.log")" "1"
check "lock removed" \
  "$([ -e "$T/.claude/skills/l-gevity-skills.lock.json" ] && echo yes || echo no)" "no"

echo
echo "== an edited instruction file is kept =="
T="$WORK/uninstall-edited-memfile"
mkdir -p "$T"
( cd "$T" && bash "$REPO_ROOT/.install/install-codex.sh" ) > /dev/null 2>&1
printf 'my rule\n' >> "$T/AGENTS.md"
uninstall_in "$T" env > "$WORK/uninstall-memfile.log" 2>&1
check "instruction file kept" "$([ -f "$T/AGENTS.md" ] && echo yes || echo no)" "yes"
check "kept file reported" \
  "$(grep -cx 'Instruction file: kept AGENTS.md (edited since install)' "$WORK/uninstall-memfile.log")" "1"

echo
echo "== a CRLF checkout of an unedited instruction file is removed =="
T="$WORK/uninstall-crlf"
mkdir -p "$T"
( cd "$T" && bash "$REPO_ROOT/.install/install-claude.sh" ) > /dev/null 2>&1
awk '{ printf "%s\r\n", $0 }' "$T/CLAUDE.md" > "$T/CLAUDE.md.tmp" && mv "$T/CLAUDE.md.tmp" "$T/CLAUDE.md"
uninstall_in "$T" env > "$WORK/uninstall-crlf.log" 2>&1
check "instruction file removed" "$([ -e "$T/CLAUDE.md" ] && echo yes || echo no)" "no"

echo
echo "== a lock path outside the tree is refused, even with a matching hash =="
T="$WORK/uninstall-traversal"
mkdir -p "$T"
( cd "$T" && bash "$REPO_ROOT/.install/install-gemini.sh" ) > /dev/null 2>&1
printf 'do not delete me\n' > "$T/CANARY.md"
awk -v entry="        \"../../CANARY.md\": \"$(sha256_of "$T/CANARY.md")\"," '
  { print }
  /^    "files": \{$/ { print entry }
' "$T/.agents/skills/l-gevity-skills.lock.json" > "$WORK/lock.tmp" &&
  mv "$WORK/lock.tmp" "$T/.agents/skills/l-gevity-skills.lock.json"
uninstall_in "$T" env > "$WORK/uninstall-traversal.log" 2>&1
check "file outside the tree survives" "$([ -f "$T/CANARY.md" ] && echo present || echo deleted)" "present"
check "refusal reported" \
  "$(grep -c 'Refused to remove unsafe path from lock: ../../CANARY.md' "$WORK/uninstall-traversal.log")" "1"

echo
echo "== a lock written before v5.7.0 leaves the instruction file to the user =="
T="$WORK/uninstall-old-lock"
mkdir -p "$T"
( cd "$T" && bash "$REPO_ROOT/.install/install-grok.sh" ) > /dev/null 2>&1
sed '/"instructionFile"/,/},/d' "$T/.agents/skills/l-gevity-skills.lock.json" > "$WORK/lock.tmp" &&
  mv "$WORK/lock.tmp" "$T/.agents/skills/l-gevity-skills.lock.json"
uninstall_in "$T" env > "$WORK/uninstall-old-lock.log" 2>&1
check "exit status" "$?" "0"
check "instruction file kept" "$([ -f "$T/GROK.md" ] && echo yes || echo no)" "yes"
check "gap reported" "$(grep -c '^Instruction file: not recorded' "$WORK/uninstall-old-lock.log")" "1"
check "skills removed" "$([ -e "$T/.agents" ] && echo yes || echo no)" "no"

if [ -n "$PYTHON" ]; then
  echo
  echo "== without Python 3, installed adapters stop the uninstall before any removal =="
  T="$WORK/uninstall-no-python"
  mkdir -p "$T"
  ( cd "$T" && bash "$REPO_ROOT/.install/install-claude.sh" ) > /dev/null 2>&1
  uninstall_in "$T" env PATH="$NOPY:$PATH" > "$WORK/uninstall-no-python.log" 2>&1
  check "exit status" "$?" "1"
  check "cause named" "$(grep -c 'Python 3 not found' "$WORK/uninstall-no-python.log")" "1"
  check "skills untouched" "$([ -f "$T/.claude/skills/alchemy/SKILL.md" ] && echo yes || echo no)" "yes"
  check "adapters untouched" "$([ -f "$T/.claude/agents/alchemy-analyst.md" ] && echo yes || echo no)" "yes"

  echo
  echo "== an edited adapter file is kept =="
  printf '\n# mine\n' >> "$T/.claude/agents/alchemy-analyst.md"
  uninstall_in "$T" env > "$WORK/uninstall-adapter.log" 2>&1
  check "exit status" "$?" "0"
  check "edited adapter kept" "$([ -f "$T/.claude/agents/alchemy-analyst.md" ] && echo yes || echo no)" "yes"
  check "unedited adapter removed" \
    "$([ -e "$T/.claude/agents/alchemy-implementer.md" ] && echo yes || echo no)" "no"
  check "adapter summary counts the kept file" \
    "$(grep -cx 'Agent-team adapters: removed; 1 kept (listed above)' "$WORK/uninstall-adapter.log")" "1"
  check "workspace profile removed" "$([ -e "$T/alchemy-workspace.json" ] && echo yes || echo no)" "no"
fi

# --- With no ref set, an installer installs the release it ships with ---
echo
echo "== the default source is this checkout's release tag =="
RELEASE="v$(grep -oE '"version": *"[^"]+"' "$REPO_ROOT/package.json" | cut -d'"' -f4)"
check "lock records the release tag as ref" \
  "$(grep -oE '"ref": "[^"]*"' "$WORK/consumer-claude/.claude/skills/l-gevity-skills.lock.json" | cut -d'"' -f4)" \
  "$RELEASE"

echo
echo "$checks checks run"
if [ "$fails" -eq 0 ]; then
  echo "Installers verified"
  exit 0
fi
echo "$fails check(s) failed"
exit 1
