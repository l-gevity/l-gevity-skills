#!/usr/bin/env bash
# l-gevity-skills installer (Claude Code)
# Usage: curl -fsSL https://raw.githubusercontent.com/l-gevity/l-gevity-skills/main/.install/install-claude.sh | bash
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
AGENT="claude"
MEMFILE="CLAUDE.md"
PRIMARY_SKILLS_DIR=".claude/skills"
# --- end agent profile ---

REPO="l-gevity/l-gevity-skills"
REF="${L_GEVITY_SKILLS_REF:-main}"
REPO_TARBALL="https://github.com/$REPO/archive/$REF.tar.gz"
TARGET="$PWD"
LOCK_NAME="l-gevity-skills.lock.json"
KNOWN_SKILL_DIRS=".claude/skills .agents/skills"
GUIDANCE_BEGIN='<!-- BEGIN L-GEVITY MANAGED GUIDANCE -->'
GUIDANCE_END='<!-- END L-GEVITY MANAGED GUIDANCE -->'

upsert_guidance() {
  dest="$1"
  input="$dest"
  if [ ! -e "$input" ]; then
    input="$TMP/empty-guidance.md"
    : > "$input"
  fi
  final_newline=0
  if [ -s "$input" ] && [ -z "$(tail -c 1 "$input")" ]; then final_newline=1; fi
  tmp="$TMP/guidance-$AGENT.md"
  # Validate before emitting anything; keep every byte outside the managed block.
  awk -v BINMODE=3 -v begin="$GUIDANCE_BEGIN" -v end="$GUIDANCE_END" -v source="$SRC/CLAUDE.md" \
      -v primary="$PRIMARY_SKILLS_DIR" \
      -v final_newline="$final_newline" -v destination="$dest" '
    BEGIN {
      while ((getline line < source) > 0) {
        sub(/\r$/, "", line)
        gsub(/\.claude\/skills/, primary, line)
        block[n++] = line
      }
      close(source)
      newline = "\n"
    }
    {
      rows[NR] = $0
      probe = $0
      if (NR == 1 && sub(/\r$/, "", probe)) newline = "\r\n"
      sub(/\r$/, "", probe)
      if (index(probe, begin)) {
        if (probe != begin || first || last) malformed = 1
        first = NR
      }
      if (index(probe, end)) {
        if (probe != end || !first || last) malformed = 1
        last = NR
      }
    }
    END {
      if (malformed || (first && !last) || (!first && last)) {
        print "Refused to update malformed L-GEVITY guidance markers in " destination > "/dev/stderr"
        exit 1
      }
      for (i = 1; i <= NR; i++) {
        if (i == first) {
          printf "%s%s", begin, newline
          for (j = 0; j < n; j++) printf "%s%s", block[j], newline
          printf "%s", end
          if (last < NR || final_newline) printf "%s", newline
          i = last
        } else {
          printf "%s", rows[i]
          if (i < NR || final_newline) printf "\n"
        }
      }
      if (!first) {
        if (NR) printf "%s", (final_newline ? newline : newline newline)
        printf "%s%s", begin, newline
        for (j = 0; j < n; j++) printf "%s%s", block[j], newline
        printf "%s%s", end, newline
      }
    }
  ' "$input" > "$tmp"
}

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

# The profile owns its root file. Stage guidance before changing skills or locks.
MEM_DEST="$TARGET/$MEMFILE"
upsert_guidance "$MEM_DEST"

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

mv "$TMP/guidance-$AGENT.md" "$MEM_DEST"
MEM_REPORT="$MEMFILE (managed L-GEVITY block updated; project guidance kept)"

echo "Installed $SKILL_COUNT skills ($FILE_COUNT files) into: $DESTS"
if [ "$REMOVED_TOTAL" -gt 0 ]; then
  echo "Removed $REMOVED_TOTAL file(s) dropped upstream."
fi
echo "Instruction file: $MEM_REPORT"
echo "Source: $REF${COMMIT:+ (commit ${COMMIT:0:7})}; per-file hashes recorded in $LOCK_NAME."
