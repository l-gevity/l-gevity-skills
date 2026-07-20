#!/usr/bin/env bash
# l-gevity-skills installer (Codex CLI / AGENTS.md)
# Usage: curl -fsSL https://raw.githubusercontent.com/l-gevity/l-gevity-skills/main/.install/install-codex.sh | bash
# Pin a version: curl -fsSL <same url> | L_GEVITY_SKILLS_REF=<branch|tag|commit> bash
set -euo pipefail

REPO="l-gevity/l-gevity-skills"
REF="${L_GEVITY_SKILLS_REF:-main}"
REPO_TARBALL="https://github.com/$REPO/archive/$REF.tar.gz"
MEMFILE="AGENTS.md"
TARGET="$PWD"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Downloading l-gevity-skills@$REF..."
curl -fsSL "$REPO_TARBALL" -o "$TMP/skills.tar.gz"
tar -xzf "$TMP/skills.tar.gz" -C "$TMP"

SRC="$(find "$TMP" -mindepth 1 -maxdepth 1 -type d -name 'l-gevity-skills-*' | head -n 1)"

COMMIT="$(curl -fsSL "https://api.github.com/repos/$REPO/commits/$REF" | grep -oE '"sha": *"[0-9a-f]{40}"' | head -n 1 | grep -oE '[0-9a-f]{40}')" || COMMIT=""
if [ -z "$COMMIT" ]; then
  echo "Warning: could not resolve $REF to a commit; lock will record the ref only."
fi

mkdir -p "$TARGET/.claude/skills"
cp -R "$SRC/.claude/skills/." "$TARGET/.claude/skills/"
SKILL_COUNT=$(find "$TARGET/.claude/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')

COMMIT_JSON="null"
[ -n "$COMMIT" ] && COMMIT_JSON="\"$COMMIT\""
{
  printf '{\n'
  printf '    "version": 1,\n'
  printf '    "source": {\n'
  printf '        "repository": "https://github.com/%s.git",\n' "$REPO"
  printf '        "ref": "%s",\n' "$REF"
  printf '        "commit": %s,\n' "$COMMIT_JSON"
  printf '        "path": ".claude/skills"\n'
  printf '    },\n'
  printf '    "syncedAt": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '    "skills": [\n'
  first=1
  while IFS= read -r name; do
    [ "$first" -eq 1 ] || printf ',\n'
    printf '        "%s"' "$name"
    first=0
  done < <(cd "$SRC/.claude/skills" && find . -mindepth 1 -maxdepth 1 -type d | sed 's|^\./||' | LC_ALL=C sort)
  printf '\n    ]\n'
  printf '}\n'
} > "$TARGET/.claude/skills/l-gevity-skills.lock.json"

if [ -e "$TARGET/$MEMFILE" ]; then
  cp "$SRC/CLAUDE.md" "$TARGET/$MEMFILE.l-gevity"
  echo "Existing $MEMFILE kept. Upstream version written to $MEMFILE.l-gevity - review and merge manually."
else
  cp "$SRC/CLAUDE.md" "$TARGET/$MEMFILE"
fi

echo "Installed $SKILL_COUNT skills + $MEMFILE (ref $REF${COMMIT:+, commit ${COMMIT:0:7}})."
