#!/usr/bin/env bash
# l-gevity-skills installer (Gemini CLI / GEMINI.md)
# Usage: curl -fsSL https://raw.githubusercontent.com/l-gevity/l-gevity-skills/main/.install/install-gemini.sh | bash
set -euo pipefail

REPO_TARBALL="https://github.com/l-gevity/l-gevity-skills/archive/refs/heads/main.tar.gz"
MEMFILE="GEMINI.md"
TARGET="$PWD"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Downloading l-gevity-skills..."
curl -fsSL "$REPO_TARBALL" -o "$TMP/skills.tar.gz"
tar -xzf "$TMP/skills.tar.gz" -C "$TMP"

SRC="$TMP/l-gevity-skills-main"

mkdir -p "$TARGET/.claude/skills"
cp -R "$SRC/.claude/skills/." "$TARGET/.claude/skills/"
SKILL_COUNT=$(find "$TARGET/.claude/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')

if [ -e "$TARGET/$MEMFILE" ]; then
  cp "$SRC/CLAUDE.md" "$TARGET/$MEMFILE.l-gevity"
  echo "Existing $MEMFILE kept. Upstream version written to $MEMFILE.l-gevity - review and merge manually."
else
  cp "$SRC/CLAUDE.md" "$TARGET/$MEMFILE"
fi

echo "Installed $SKILL_COUNT skills + $MEMFILE."
