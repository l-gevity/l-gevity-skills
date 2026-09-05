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
echo "$checks checks run"
if [ "$fails" -eq 0 ]; then
  echo "Installers verified"
  exit 0
fi
echo "$fails check(s) failed"
exit 1
