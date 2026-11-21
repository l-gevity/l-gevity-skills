#!/usr/bin/env python3
"""Copy a package's hand-off out of its agent's final reply, byte for byte.

A read-only agent cannot write its hand-off, and a lead that re-types a 20 KB
JSON block from the reply copies it with errors. This script takes the reply
from a file instead: a plain-text reply, or a JSON Lines transcript, where it
reads the last assistant message that holds text. That message must hold
exactly one fenced block whose JSON carries the alchemy-handoff/1 schema; the
block is written unchanged, so the hand-off check sees what the agent wrote.
An earlier message is never used: a draft the agent replaced is not its
hand-off.

Usage:
    extract_handoff.py <reply or transcript> --out <state_dir>/<run>/handoffs/<package>.json

Exit 0 written, 1 no single hand-off in the final reply, 2 bad arguments or
unreadable input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HANDOFF_SCHEMA = "alchemy-handoff/1"
OPEN = re.compile(r"^ {0,3}(`{3,})[ \t]*([^`]*?)[ \t]*$")


class InputError(Exception):
    pass


def _text_of(content: Any) -> str:
    """The text parts of a message's content: a string, or a list of parts."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(part["text"] for part in content
                         if isinstance(part, dict) and isinstance(part.get("text"), str))
    return ""


def _assistant_text(record: Any) -> str | None:
    """Text of one transcript line when it is an assistant message, else None.
    The message sits at the top level or under `message` or `payload`."""
    if not isinstance(record, dict):
        return None
    for message in (record, record.get("message"), record.get("payload")):
        if isinstance(message, dict) and message.get("role") == "assistant":
            return _text_of(message.get("content"))
    return None


def final_reply(raw: str) -> str:
    """The reply itself, or the last assistant text of a JSON Lines transcript."""
    lines = [line for line in raw.splitlines() if line.strip()]
    try:
        records = [json.loads(line) for line in lines]
    except json.JSONDecodeError:
        return raw
    if not records or not all(isinstance(record, dict) for record in records):
        return raw
    if not any(_assistant_text(record) is not None for record in records):
        return raw  # JSON, but no transcript: the reply is the hand-off itself
    texts = [text for text in (_assistant_text(record) for record in records) if text and text.strip()]
    if not texts:
        raise InputError("the transcript holds no assistant message with text")
    return texts[-1]


def fenced_blocks(reply: str) -> list[tuple[str, str]]:
    """(info string, content) of each fenced code block. Fences pair by line,
    so a closing fence is never read as the opening of the next block."""
    blocks: list[tuple[str, str]] = []
    fence, info, body = None, "", []
    for line in reply.splitlines(keepends=True):
        bare = line.rstrip("\r\n")
        if fence is None:
            match = OPEN.match(bare)
            if match:
                fence, info, body = match.group(1), match.group(2).lower(), []
        elif bare.strip().startswith(fence) and not bare.strip().strip("`"):
            blocks.append((info, "".join(body)))
            fence = None
        else:
            body.append(line)
    return blocks


def handoff_block(reply: str) -> str:
    """The one fenced block in the reply whose JSON is a hand-off."""
    blocks = fenced_blocks(reply)
    if not blocks:
        # A reply that is nothing but the record needs no fence.
        try:
            whole = json.loads(reply)
        except json.JSONDecodeError:
            whole = None
        if isinstance(whole, dict) and whole.get("schema") == HANDOFF_SCHEMA:
            return reply.strip()
    found = []
    for info, body in blocks:
        if info not in ("", "json"):
            continue
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("schema") == HANDOFF_SCHEMA:
            found.append(body)
    if len(found) != 1:
        raise LookupError(f"the final reply holds {len(found)} fenced {HANDOFF_SCHEMA} blocks that parse; "
                          "it must hold exactly one: return the package to its owner")
    return found[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Copy the hand-off out of an agent's final reply.")
    parser.add_argument("reply", type=Path, help="the reply as text, or the agent's JSON Lines transcript")
    parser.add_argument("--out", type=Path, required=True, help="where to write the hand-off JSON")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    try:
        try:
            raw = args.reply.read_text(encoding="utf-8")
        except OSError as exc:
            raise InputError(f"{args.reply}: {exc.strerror or exc}") from exc
        block = handoff_block(final_reply(raw))
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except LookupError as exc:
        print(f"NOT FOUND: {exc}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(block.encode("utf-8"))
    print(f"{args.out}: wrote {len(block.encode('utf-8'))} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
