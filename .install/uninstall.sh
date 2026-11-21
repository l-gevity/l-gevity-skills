#!/usr/bin/env bash
# l-gevity-skills uninstaller (every agent)
# Usage: curl -fsSL https://raw.githubusercontent.com/l-gevity/l-gevity-skills/main/.install/uninstall.sh | bash
#
# Run from the project root. Removes what the installers wrote, from the
# records they left, and needs no network:
#   1. the agent-team adapters, through the installed init_workspace.py --uninstall;
#   2. the instruction file the lock names, while its digest still matches;
#   3. every file in each skills tree's lock whose sha256 still matches, then the lock.
# An edited file is kept and reported. A step that cannot run stops the
# uninstall before the skills trees, which hold the adapter remover, are touched.
set -euo pipefail

TARGET="$PWD"
LOCK_NAME="l-gevity-skills.lock.json"
KNOWN_SKILL_DIRS=".claude/skills .agents/skills"
KNOWN_MEMFILES="CLAUDE.md AGENTS.md GEMINI.md GROK.md"
PROFILE_NAME="alchemy-workspace.json"
INIT_REL="alchemy-orchestrate/scripts/init_workspace.py"

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | cut -d' ' -f1
  else
    echo "Error: neither sha256sum nor shasum is available; cannot check what is unedited." >&2
    exit 1
  fi
}

# Digest of a text file with line endings ignored, as the installers record it.
text_digest() {
  printf '%s' "$(tr -d '\r' < "$1")" > "$TMP/digest.txt"
  printf 'sha256:%s' "$(sha256_of "$TMP/digest.txt")"
}

# The lock lives in the consumer's repo and drives a delete. Treat its keys as
# untrusted: a hand-edited or corrupted lock must not reach outside the tree.
safe_relpath() {
  case "$1" in
    "" | /* | *\\* | *:*) return 1 ;;
  esac
  case "/$1/" in
    */../*) return 1 ;;
  esac
  return 0
}

# Python 3 under either of its usual names. A bare `python` may be Python 2,
# and on Windows `python3` may be a stub that only prints an install hint.
python3_command() {
  for candidate in python3 python; do
    if "$candidate" -c 'import sys; sys.exit(sys.version_info[0] != 3)' >/dev/null 2>&1; then
      printf '%s' "$candidate"
      return 0
    fi
  done
  return 1
}

TMP="$(mktemp -d 2>/dev/null || true)"
case "${TMP:-}" in
  "" | [A-Za-z]:*) TMP="$(TMPDIR=/tmp mktemp -d)" ;;
esac
trap 'rm -rf "$TMP"' EXIT

LOCKED=""
for d in $KNOWN_SKILL_DIRS; do
  if [ -f "$TARGET/$d/$LOCK_NAME" ]; then
    LOCKED="${LOCKED:+$LOCKED }$d"
  fi
done
if [ -z "$LOCKED" ]; then
  echo "Nothing to uninstall: no $LOCK_NAME in $KNOWN_SKILL_DIRS under $TARGET."
  exit 0
fi

# --- 1. Agent-team adapters ---
INIT=""
for d in $LOCKED; do
  if [ -z "$INIT" ] && [ -f "$TARGET/$d/$INIT_REL" ]; then
    INIT="$d/$INIT_REL"
  fi
done
PYTHON="$(python3_command || true)"
ADAPTER_REPORT="none recorded (no $PROFILE_NAME)"
if [ -n "$INIT" ] && [ -n "$PYTHON" ]; then
  echo "Removing agent-team adapters..."
  if ! "$PYTHON" "$TARGET/$INIT" --uninstall --runtime all --root "$TARGET" > "$TMP/adapters.txt"; then
    sed 's/^/  /' "$TMP/adapters.txt"
    echo "Error: $INIT --uninstall failed (see above); nothing else was removed." >&2
    echo "An install older than v5.7.0 has no --uninstall: run the installer once to update, then uninstall again." >&2
    exit 1
  fi
  sed 's/^/  /' "$TMP/adapters.txt"
  KEPT_ADAPTERS="$(grep -c ': kept' "$TMP/adapters.txt" || true)"
  ADAPTER_REPORT="removed"
  if [ "$KEPT_ADAPTERS" -gt 0 ]; then
    ADAPTER_REPORT="removed; $KEPT_ADAPTERS kept (listed above)"
  fi
elif [ -f "$TARGET/$PROFILE_NAME" ]; then
  # The adapters were installed, and only init_workspace.py knows which files
  # they are. Removing the skills now would delete the one tool that can tell.
  if [ -z "$PYTHON" ]; then
    echo "Error: Python 3 not found; it is needed to remove the agent-team adapters. Nothing was removed." >&2
  else
    echo "Error: $INIT_REL not found in $LOCKED; cannot remove the agent-team adapters. Nothing was removed." >&2
  fi
  exit 1
fi

# --- 2. The instruction file each lock names ---
MEM_REPORT="not recorded (installed before v5.7.0); delete it by hand if you did not edit it"
SEEN=""
for d in $LOCKED; do
  record="$(tr -d '\r\n' < "$TARGET/$d/$LOCK_NAME" | grep -oE '"instructionFile" *: *\{[^}]*\}' || true)"
  [ -n "$record" ] || continue
  path="$(printf '%s' "$record" | sed -nE 's/.*"path" *: *"([^"]*)".*/\1/p')"
  want="$(printf '%s' "$record" | sed -nE 's/.*"digest" *: *"(sha256:[0-9a-f]{64})".*/\1/p')"
  allowed=""
  for name in $KNOWN_MEMFILES; do
    if [ "$path" = "$name" ] || [ "$path" = "$name.l-gevity" ]; then
      allowed="yes"
    fi
  done
  if [ -z "$allowed" ]; then
    echo "Refused to remove instruction file named by $d/$LOCK_NAME: $path" >&2
    continue
  fi
  case " $SEEN " in
    *" $path "*) continue ;;
  esac
  SEEN="${SEEN:+$SEEN }$path"
  if [ ! -f "$TARGET/$path" ]; then
    MEM_REPORT="$path (already gone)"
  elif [ -n "$want" ] && [ "$(text_digest "$TARGET/$path")" = "$want" ]; then
    rm -f "$TARGET/$path"
    MEM_REPORT="removed $path"
  else
    MEM_REPORT="kept $path (edited since install)"
  fi
done

# --- 3. Skills trees ---
REMOVED_TOTAL=0
KEPT_TOTAL=0
KEPT_TREES=""
for d in $LOCKED; do
  dest="$TARGET/$d"
  lock="$dest/$LOCK_NAME"
  grep -oE '"[^"]+" *: *"[0-9a-f]{64}"' "$lock" > "$TMP/entries.txt" || true
  if [ ! -s "$TMP/entries.txt" ]; then
    echo "Kept $d: its lock records no file hashes (a v1 lock). Run the installer once to update it, then uninstall again."
    KEPT_TREES="${KEPT_TREES:+$KEPT_TREES }$d"
    continue
  fi
  while IFS= read -r entry; do
    rel="$(printf '%s' "$entry" | sed -E 's/^"([^"]+)".*/\1/')"
    want="$(printf '%s' "$entry" | sed -E 's/.*"([0-9a-f]{64})"$/\1/')"
    if ! safe_relpath "$rel"; then
      echo "Refused to remove unsafe path from lock: $rel" >&2
      continue
    fi
    [ -f "$dest/$rel" ] || continue
    if [ "$(sha256_of "$dest/$rel")" = "$want" ]; then
      rm -f "$dest/$rel"
      REMOVED_TOTAL=$((REMOVED_TOTAL + 1))
    else
      echo "Kept (edited since install): $d/$rel"
      KEPT_TOTAL=$((KEPT_TOTAL + 1))
    fi
  done < "$TMP/entries.txt"
  rm -f "$lock"
  # Bytecode caches are regenerated on demand and keep a directory from
  # emptying. Then remove what is left empty, deepest first.
  find "$dest" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
  find "$dest" -depth -type d -empty -exec rmdir {} \; 2>/dev/null || true
  rmdir "$(dirname "$dest")" 2>/dev/null || true
done

echo "Removed $REMOVED_TOTAL file(s) from: $LOCKED"
if [ "$KEPT_TOTAL" -gt 0 ]; then
  echo "Kept $KEPT_TOTAL edited file(s), listed above."
fi
if [ -n "$KEPT_TREES" ]; then
  echo "Not uninstalled: $KEPT_TREES"
fi
echo "Instruction file: $MEM_REPORT"
echo "Agent-team adapters: $ADAPTER_REPORT"
