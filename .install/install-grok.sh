#!/usr/bin/env bash
# l-gevity-skills installer (Grok CLI / GROK.md)
# Usage: curl -fsSL https://raw.githubusercontent.com/l-gevity/l-gevity-skills/main/.install/install-grok.sh | bash
# Pin a version: curl -fsSL <same url> | L_GEVITY_SKILLS_REF=<branch|tag|commit> bash
#
# Lock format v2 records a sha256 for every file it writes, and a later run
# removes files that upstream has since dropped. That pruning reads the file
# map from the lock already on disk, so upgrading FROM a v1 lock (which has no
# map) prunes nothing on that first run — removals begin from the second.
#
# Test seam: L_GEVITY_SKILLS_ARCHIVE=<path or url> installs from that archive
# instead of GitHub, and skips commit resolution. Used by
# scripts/test-installers.sh so CI needs no network.
set -euo pipefail

# --- agent profile ---
AGENT="grok"
MEMFILE="GROK.md"
PRIMARY_SKILLS_DIR=".agents/skills"
# --- end agent profile ---

REPO="l-gevity/l-gevity-skills"
REF="${L_GEVITY_SKILLS_REF:-main}"
REPO_TARBALL="https://github.com/$REPO/archive/$REF.tar.gz"
TARGET="$PWD"
LOCK_NAME="l-gevity-skills.lock.json"
KNOWN_SKILL_DIRS=".claude/skills .agents/skills"
KNOWN_MEMFILES="CLAUDE.md AGENTS.md GEMINI.md GROK.md"

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | cut -d' ' -f1
  else
    echo "Error: neither sha256sum nor shasum is available; cannot hash the install." >&2
    exit 1
  fi
}

# Files this installer recorded in a previous run, from that run's lock.
previous_files() {
  lock="$1/$LOCK_NAME"
  if [ -f "$lock" ]; then
    grep -oE '"[^"]+" *: *"[0-9a-f]{64}"' "$lock" | sed -E 's/^"([^"]+)".*/\1/'
  fi
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

# A Windows-style TMPDIR makes tar read the leading "C:" as a remote host.
TMP="$(mktemp -d 2>/dev/null || true)"
case "${TMP:-}" in
  "" | [A-Za-z]:*) TMP="$(TMPDIR=/tmp mktemp -d)" ;;
esac
trap 'rm -rf "$TMP"' EXIT

TAR_LOCAL=""
if tar --help 2>&1 | grep -q -- '--force-local'; then
  TAR_LOCAL="--force-local"
fi

ARCHIVE="${L_GEVITY_SKILLS_ARCHIVE:-}"
if [ -n "$ARCHIVE" ] && [ -f "$ARCHIVE" ]; then
  echo "Installing l-gevity-skills from $ARCHIVE..."
  cp "$ARCHIVE" "$TMP/skills.tar.gz"
else
  echo "Downloading l-gevity-skills@$REF..."
  curl -fsSL "${ARCHIVE:-$REPO_TARBALL}" -o "$TMP/skills.tar.gz"
fi
tar -xzf "$TMP/skills.tar.gz" $TAR_LOCAL -C "$TMP"

SRC="$(find "$TMP" -mindepth 1 -maxdepth 1 -type d -name 'l-gevity-skills-*' | head -n 1)"
SRC_SKILLS="$SRC/.claude/skills"

COMMIT=""
if [ -z "$ARCHIVE" ]; then
  COMMIT="$(curl -fsSL "https://api.github.com/repos/$REPO/commits/$REF" | grep -oE '"sha": *"[0-9a-f]{40}"' | head -n 1 | grep -oE '[0-9a-f]{40}')" || COMMIT=""
  if [ -z "$COMMIT" ]; then
    echo "Warning: could not resolve $REF to a commit; lock will record the ref only."
  fi
fi

# Report what upstream ships, never what the target happens to contain.
SRC_FILES="$(cd "$SRC_SKILLS" && find . -type f ! -name '*.pyc' ! -name '*.pyo' | sed 's|^\./||' | LC_ALL=C sort)"
SRC_SKILL_NAMES="$(cd "$SRC_SKILLS" && find . -mindepth 1 -maxdepth 1 -type d | sed 's|^\./||' | LC_ALL=C sort)"
SKILL_COUNT="$(printf '%s\n' "$SRC_SKILL_NAMES" | grep -c . || true)"
FILE_COUNT="$(printf '%s\n' "$SRC_FILES" | grep -c . || true)"

HASHES="$TMP/hashes.txt"
: > "$HASHES"
while IFS= read -r rel; do
  if [ -n "$rel" ]; then
    printf '%s  %s\n' "$(sha256_of "$SRC_SKILLS/$rel")" "$rel" >> "$HASHES"
  fi
done <<EOF
$SRC_FILES
EOF

# Install into the profile's tree, plus any sibling tree the consumer already keeps.
DESTS="$PRIMARY_SKILLS_DIR"
for d in $KNOWN_SKILL_DIRS; do
  if [ "$d" != "$PRIMARY_SKILLS_DIR" ] && [ -d "$TARGET/$d" ]; then
    DESTS="$DESTS $d"
  fi
done

DESTS_JSON=""
for d in $DESTS; do
  if [ -n "$DESTS_JSON" ]; then
    DESTS_JSON="$DESTS_JSON, "
  fi
  DESTS_JSON="$DESTS_JSON\"$d\""
done

COMMIT_JSON="null"
if [ -n "$COMMIT" ]; then
  COMMIT_JSON="\"$COMMIT\""
fi
SYNCED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

write_lock() {
  dest_abs="$1"
  {
    printf '{\n'
    printf '    "version": 2,\n'
    printf '    "source": {\n'
    printf '        "repository": "https://github.com/%s.git",\n' "$REPO"
    printf '        "ref": "%s",\n' "$REF"
    printf '        "commit": %s,\n' "$COMMIT_JSON"
    printf '        "path": ".claude/skills"\n'
    printf '    },\n'
    printf '    "agent": "%s",\n' "$AGENT"
    printf '    "installedTo": [%s],\n' "$DESTS_JSON"
    printf '    "syncedAt": "%s",\n' "$SYNCED_AT"
    printf '    "skills": [\n'
    first=1
    while IFS= read -r name; do
      if [ -n "$name" ]; then
        if [ "$first" -eq 1 ]; then first=0; else printf ',\n'; fi
        printf '        "%s"' "$name"
      fi
    done <<INNER
$SRC_SKILL_NAMES
INNER
    printf '\n    ],\n'
    printf '    "files": {\n'
    first=1
    while IFS= read -r line; do
      if [ -n "$line" ]; then
        if [ "$first" -eq 1 ]; then first=0; else printf ',\n'; fi
        printf '        "%s": "%s"' "${line#*  }" "${line%%  *}"
      fi
    done < "$HASHES"
    printf '\n    }\n'
    printf '}\n'
  } > "$dest_abs/$LOCK_NAME"
}

REMOVED_TOTAL=0
for d in $DESTS; do
  dest="$TARGET/$d"
  mkdir -p "$dest"
  OLD="$TMP/old-$(printf '%s' "$d" | tr '/.' '__').txt"
  previous_files "$dest" | LC_ALL=C sort > "$OLD" || true
  cp -R "$SRC_SKILLS/." "$dest/"
  # Anything this installer wrote before and upstream has since dropped.
  while IFS= read -r rel; do
    if [ -n "$rel" ] && ! printf '%s\n' "$SRC_FILES" | grep -qxF "$rel"; then
      if ! safe_relpath "$rel"; then
        echo "Refused to remove unsafe path from lock: $rel" >&2
        continue
      fi
      rm -f "$dest/$rel"
      parent="$(dirname "$dest/$rel")"
      if [ "$parent" != "$dest" ]; then
        rmdir "$parent" 2>/dev/null || true
      fi
      echo "Removed (dropped upstream): $d/$rel"
      REMOVED_TOTAL=$((REMOVED_TOTAL + 1))
    fi
  done < "$OLD"
  write_lock "$dest"
done

# Honor whichever instruction file the project already uses, whatever its name.
EXISTING_MEM=""
for name in $KNOWN_MEMFILES; do
  if [ -z "$EXISTING_MEM" ] && [ -e "$TARGET/$name" ]; then
    EXISTING_MEM="$name"
  fi
done
if [ -n "$EXISTING_MEM" ]; then
  cp "$SRC/CLAUDE.md" "$TARGET/$EXISTING_MEM.l-gevity"
  MEM_REPORT="$EXISTING_MEM.l-gevity (existing $EXISTING_MEM kept; review and merge manually)"
else
  cp "$SRC/CLAUDE.md" "$TARGET/$MEMFILE"
  MEM_REPORT="$MEMFILE"
fi

echo "Installed $SKILL_COUNT skills ($FILE_COUNT files) into: $DESTS"
if [ "$REMOVED_TOTAL" -gt 0 ]; then
  echo "Removed $REMOVED_TOTAL file(s) dropped upstream."
fi
echo "Instruction file: $MEM_REPORT"
echo "Source: $REF${COMMIT:+ (commit ${COMMIT:0:7})}; per-file hashes recorded in $LOCK_NAME."
