#!/usr/bin/env python3
"""Deterministic replay invariants; no model or signed-in CLI is required."""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPOSITORY = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("replay_scenarios", REPOSITORY / "scripts" / "replay-scenarios.py")
assert SPEC and SPEC.loader
replay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(replay)


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="l-gevity-replay-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.before = self.root / "original-source"
        self.after = self.root / "candidate-source"
        for source, text in ((self.before, "baseline root"), (self.after, "candidate root")):
            (source / ".claude" / "skills" / "alchemy" / "references").mkdir(parents=True)
            (source / "CLAUDE.md").write_text(text, encoding="utf-8")
            (source / ".claude" / "skills" / "alchemy" / "SKILL.md").write_text("dispatch core guide", encoding="utf-8")
            (source / ".claude" / "skills" / "alchemy" / "references" / "one.md").write_text("reference one guide", encoding="utf-8")
            (source / ".claude" / "skills" / "alchemy" / "references" / "two.md").write_text("reference two guide", encoding="utf-8")
        self.directory = self.root / ".scenarios" / "case"
        (self.directory / "project").mkdir(parents=True)
        (self.directory / "project" / "input.txt").write_text("identical fixture", encoding="utf-8")
        self.scenario = {
            "request": "Use /alchemy to assess this product fixture.", "skills": ["alchemy"],
            "expect": [{"id": "decision", "criterion": "dispatch #1: retains a decision", "check": "field_in", "field": "Decision", "values": ["SKIP"]}],
            "blind_judge_rubric": ["Does the decision follow the request and raw fixture?"]
        }
        (self.directory / "scenario.json").write_bytes(replay.json_bytes(self.scenario))
        (self.root / "scripts").mkdir()
        (self.root / "scripts" / "validate-skills.py").write_bytes((REPOSITORY / "scripts" / "validate-skills.py").read_bytes())
        self.destination = self.directory / "replays" / "trial.json"
        self.args = argparse.Namespace(scenario="case", before=str(self.before), after=str(self.after), runs=3,
                                       seed=42, blind_judge=True, judge_model=None, model=None, timeout=30, judge_timeout=30)
        self.root_patch = patch.object(replay, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.calls = []

    def freeze(self):
        artifact = replay.freeze(self.args, self.destination)
        replay.persist(self.destination, artifact)
        return artifact

    def cli(self, command, cwd, stdout, stderr, timeout, stdin=None):
        stderr.write_text("", encoding="utf-8")
        if "--safe-mode" in command:
            self.calls.append(("judge", command, sorted(cwd.iterdir())))
            self.assertEqual(sorted(cwd.iterdir()), [])
            self.assertEqual(command[command.index("--tools") + 1], "")
            self.assertEqual(command[command.index("--setting-sources") + 1], "")
            self.assertNotIn("--allowedTools", command)
            self.assertIsInstance(stdin, bytes)
            self.assertLess(len(command[command.index("-p") + 1]), 200)
            prompt = stdin.decode("utf-8")
            self.assertNotIn("original-source", prompt)
            self.assertNotIn("candidate-source", prompt)
            self.assertNotIn("baseline root", prompt)
            self.assertNotIn("candidate root", prompt)
            self.assertIn(self.scenario["request"], prompt)
            self.assertIn("identical fixture", prompt)
            context = json.loads(prompt.split("<shared-request-and-product-fixture>\n", 1)[1].split("\n</shared-request-and-product-fixture>", 1)[0])
            self.assertEqual(set(context["product_tool_provenance"]), {"A", "B"})
            for provenance in context["product_tool_provenance"].values():
                self.assertEqual(provenance["observations"][0]["result"], "No matches found")
                self.assertEqual(provenance["observations"][0]["status"], "success")
                self.assertEqual(provenance["files_read"], ["input.txt"])
            stdout.write_text('{"A": {"criterion": true}, "B": {"criterion": true}, "preference": "tie", "reason": "Both follow the request."}', encoding="utf-8")
            return 0, None
        self.assertEqual(command[command.index("-p") + 1], self.scenario["request"])
        self.assertEqual((cwd / "input.txt").read_text(encoding="utf-8"), "identical fixture")
        root_text = (cwd / "CLAUDE.md").read_text(encoding="utf-8")
        self.calls.append(("arm", root_text, command))
        events = [
            {"type": "system", "subtype": "init", "cwd": str(cwd), "model": "mock", "skills": ["alchemy"]},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": "alchemy"}},
                {"type": "tool_use", "name": "Read", "input": {"file_path": str(cwd / ".claude" / "skills" / "alchemy" / "SKILL.md")}},
                {"type": "tool_use", "name": "Read", "input": {"file_path": str(cwd / ".claude" / "skills" / "alchemy" / "references" / "one.md")}},
                {"type": "tool_use", "name": "Read", "input": {"file_path": str(cwd / ".claude" / "skills" / "alchemy" / "references" / "one.md")}},
                {"type": "tool_use", "name": "Read", "input": {"file_path": str(cwd / ".claude" / "skills" / "alchemy" / "references" / "two.md")}},
                {"type": "tool_use", "id": "product-search", "name": "Grep", "input": {"pattern": "old-color", "path": str(cwd), "output_mode": "content"}},
                {"type": "tool_use", "id": "product-read", "name": "Read", "input": {"file_path": str(cwd / "input.txt")}},
                {"type": "text", "text": "Decision: SKIP\nDecisive evidence: identical fixture.\nNext action: keep the requested behavior."}
            ]}},
            {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "product-search", "content": "No matches found"},
                {"type": "tool_result", "tool_use_id": "product-read", "content": "identical fixture"}
            ]}},
            {"type": "result", "num_turns": 2, "is_error": False}
        ]
        stdout.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")
        return 0, None

    def test_unique_guidance_counts_skill_read_mirror_and_all_references(self):
        counts = {"CLAUDE.md": 10, "alchemy/SKILL.md": 20, "alchemy/references/one.md": 30, "alchemy/references/two.md": 40}
        transcript = {"skills_invoked": ["alchemy", "library:alchemy"], "files_read": [
            "CLAUDE.md", ".claude/skills/alchemy/SKILL.md", ".agents/skills/alchemy/SKILL.md",
            ".claude/skills/alchemy/references/one.md", ".claude/skills/alchemy/references/one.md",
            ".claude\\skills\\alchemy\\references\\two.md"],
            "paths_searched": [".claude/skills/other/SKILL.md"]}
        result = replay.loaded_guidance(transcript, counts)
        self.assertEqual(result["loaded_guidance_words_estimate"], 100)
        self.assertEqual(result["loaded_guidance_files"], sorted(counts))
        self.assertEqual(result["unresolved_guidance_files"], [])
        transcript["skills_invoked"].append("external:missing")
        self.assertEqual(replay.loaded_guidance(transcript, counts)["unresolved_guidance_files"], ["missing/SKILL.md"])

    def test_frozen_sources_fixture_request_criteria_randomized_order_and_blind_judge(self):
        artifact = self.freeze()
        self.assertNotEqual(artifact["sources"]["before"]["content_sha256"], artifact["sources"]["after"]["content_sha256"])
        self.assertEqual(len(artifact["runs"]), 3)
        self.assertEqual({tuple(pair["arm_order"]) for pair in artifact["runs"]}, {("before", "after"), ("after", "before")})
        # Live changes after freezing must affect neither the requests nor arms.
        (self.before / "CLAUDE.md").write_text("mutated live source", encoding="utf-8")
        (self.after / "CLAUDE.md").write_text("mutated live source", encoding="utf-8")
        (self.directory / "project" / "input.txt").write_text("mutated fixture", encoding="utf-8")
        (self.directory / "scenario.json").write_text("{}", encoding="utf-8")
        (self.root / "scripts" / "validate-skills.py").write_text("raise RuntimeError('live checker changed')", encoding="utf-8")
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=self.cli):
            self.assertEqual(replay.execute(artifact, self.destination), 0)
        recorded = json.loads(self.destination.read_text(encoding="utf-8"))
        self.assertEqual(recorded["completed_pairs"], 3)
        self.assertEqual(recorded["criteria"], self.scenario["expect"])
        self.assertEqual(recorded["status"], "complete")
        self.assertEqual(len([call for call in self.calls if call[0] == "judge"]), 3)
        for pair in recorded["runs"]:
            for arm in ("before", "after"):
                result = pair["arms"][arm]
                self.assertTrue(all(result["expectations"].values()))
                self.assertEqual(result["loaded_guidance_words_estimate"], 11)
                self.assertEqual(result["content_sha256"], artifact["sources"][arm]["content_sha256"])
                self.assertTrue((self.destination.parent / result["stdout_file"]).is_file())
                self.assertEqual(result["transcript"]["recorded_with"], "claude-code unknown, model mock")
            packet = json.loads((self.destination.parent / pair["judge_packet_file"]).read_text(encoding="utf-8"))
            self.assertEqual(set(packet), {"rubric", "reports", "context"})
            self.assertEqual(set(packet["reports"]), {"A", "B"})
            self.assertNotIn("judge_key", packet)

    def test_interrupt_retains_completed_pair_and_arm_and_resume_reuses_them(self):
        artifact = self.freeze()
        counter = 0
        def interrupted_cli(command, cwd, stdout, stderr, timeout, stdin=None):
            nonlocal counter
            if "--safe-mode" not in command:
                counter += 1
                if counter == 4:
                    stdout.write_text('{"type":"partial"}\n', encoding="utf-8")
                    stderr.write_text("", encoding="utf-8")
                    raise KeyboardInterrupt()
            return self.cli(command, cwd, stdout, stderr, timeout, stdin=stdin)
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=interrupted_cli):
            self.assertEqual(replay.execute(artifact, self.destination), 130)
        saved = json.loads(self.destination.read_text(encoding="utf-8"))
        self.assertEqual(saved["completed_pairs"], 1)
        self.assertEqual(saved["status"], "interrupted")
        second_pair = saved["runs"][1]
        self.assertEqual(second_pair["arms"][second_pair["arm_order"][0]]["status"], "complete")
        interrupted = second_pair["arms"][second_pair["arm_order"][1]]
        self.assertEqual(interrupted["status"], "interrupted")
        self.assertIn("partial", (self.destination.parent / interrupted["stdout_file"]).read_text(encoding="utf-8"))
        self.calls.clear()
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=self.cli):
            self.assertEqual(replay.main(["--resume", str(self.destination)]), 0)
        self.assertEqual(len([call for call in self.calls if call[0] == "arm"]), 3)
        self.assertEqual(len([call for call in self.calls if call[0] == "judge"]), 2)
        resumed = json.loads(self.destination.read_text(encoding="utf-8"))
        retried = resumed["runs"][1]["arms"][second_pair["arm_order"][1]]
        self.assertEqual(retried["previous_attempts"][0]["status"], "interrupted")
        self.assertIn("partial", (self.destination.parent / retried["previous_attempts"][0]["stdout_file"]).read_text(encoding="utf-8"))

    def test_failed_arm_and_judge_errors_remain_incomplete_and_resumable(self):
        artifact = self.freeze()
        count = 0
        def failed_cli(command, cwd, stdout, stderr, timeout, stdin=None):
            nonlocal count
            count += 1
            if count == 1:
                stdout.write_text("partial", encoding="utf-8")
                stderr.write_text("agent failed", encoding="utf-8")
                return 1, None
            if "--safe-mode" in command:
                stdout.write_text("", encoding="utf-8")
                stderr.write_text("judge failed", encoding="utf-8")
                return 1, None
            return self.cli(command, cwd, stdout, stderr, timeout, stdin=stdin)
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=failed_cli):
            self.assertEqual(replay.execute(artifact, self.destination), 1)
        self.assertEqual(artifact["status"], "incomplete")
        self.assertEqual(artifact["completed_pairs"], 2)
        self.assertEqual(artifact["runs"][0]["status"], "incomplete")
        self.assertIn("blind_judge_error", artifact["runs"][1])
        self.calls.clear()
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=self.cli):
            self.assertEqual(replay.execute(artifact, self.destination), 0)
        self.assertEqual(len([call for call in self.calls if call[0] == "arm"]), 1)
        self.assertEqual(len([call for call in self.calls if call[0] == "judge"]), 3)

    def test_reject_modified_frozen_source_fixture_and_criteria(self):
        artifact = self.freeze()
        artifact["criteria"] = []
        with self.assertRaisesRegex(ValueError, "criteria"):
            replay.execute(artifact, self.destination)
        artifact["criteria"] = self.scenario["expect"]
        inputs = self.destination.parent / artifact["inputs_directory"]
        (inputs / "after" / "CLAUDE.md").write_text("tampered", encoding="utf-8")
        (inputs / "fixture" / "input.txt").write_text("tampered", encoding="utf-8")
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=self.cli):
            self.assertEqual(replay.execute(artifact, self.destination), 1)
        self.assertFalse(self.calls)
        errors = [result["error"] for pair in artifact["runs"] for result in pair["arms"].values()]
        self.assertTrue(any("source was modified" in message for message in errors))
        self.assertTrue(any("fixture was modified" in message for message in errors))

    def test_fixture_cannot_override_guidance_or_settings(self):
        (self.directory / "project" / "CLAUDE.md").write_text("override", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "override agent guidance"):
            self.freeze()

    def test_git_revision_source_preserves_exact_content_and_references(self):
        with tempfile.TemporaryDirectory(prefix="l-gevity-replay-git-test-") as temporary:
            directory = Path(temporary)
            with patch.object(replay, "ROOT", REPOSITORY):
                info = replay.copy_source("HEAD", directory / "guidance", directory)
            expected = subprocess.run(["git", "show", "HEAD:CLAUDE.md"], cwd=REPOSITORY, capture_output=True, check=True).stdout
            self.assertEqual((directory / "guidance" / "CLAUDE.md").read_bytes(), expected)
            self.assertTrue(info["source"].startswith("git:"))
            self.assertEqual(info["content_sha256"], replay.content_hash(replay.manifest(directory / "guidance")))
            self.assertTrue(any("/references/" in filename for filename in info["guidance_word_counts"]))

    def test_capture_keeps_stdout_stderr_and_timeout(self):
        stdout, stderr = self.root / "raw.stdout", self.root / "raw.stderr"
        code, error = replay.capture([sys.executable, "-c", "import sys; print('trace'); print('diagnostic', file=sys.stderr); sys.exit(4)"], self.root, stdout, stderr, 10)
        self.assertEqual(code, 4)
        self.assertIsNone(error)
        self.assertIn("trace", stdout.read_text(encoding="utf-8"))
        self.assertIn("diagnostic", stderr.read_text(encoding="utf-8"))
        code, error = replay.capture([sys.executable, "-c", "import time; print('partial', flush=True); time.sleep(10)"], self.root, stdout, stderr, 1)
        self.assertIsNone(code)
        self.assertIn("exceeded", error)
        self.assertIn("partial", stdout.read_text(encoding="utf-8"))

    def test_fixture_context_reports_omissions_explicitly(self):
        (self.directory / "project" / "binary.bin").write_bytes(b"\xff")
        context = replay.fixture_context(self.directory / "project", limit=1)
        self.assertEqual(context["files"], [])
        self.assertEqual(len(context["omitted"]), 2)

    def test_failed_tool_loads_excluded_successful_retry_still_counts(self):
        skill_path = str(self.root / ".claude" / "skills" / "alchemy" / "SKILL.md")
        reference_path = str(self.root / ".claude" / "skills" / "alchemy" / "references" / "one.md")
        events = [
            {"message": {"content": [
                {"type": "tool_use", "id": "one", "name": "Read", "input": {"file_path": skill_path}},
                {"type": "tool_use", "id": "two", "name": "Read", "input": {"file_path": reference_path}},
                {"type": "tool_use", "id": "three", "name": "Read", "input": {"file_path": reference_path}},
                {"type": "tool_use", "id": "four", "name": "Skill", "input": {"skill": "missing"}}]}},
            {"message": {"content": [
                {"type": "tool_result", "tool_use_id": "one", "is_error": True},
                {"type": "tool_result", "tool_use_id": "two", "is_error": True},
                {"type": "tool_result", "tool_use_id": "three", "is_error": False},
                {"type": "tool_result", "tool_use_id": "four", "is_error": True}]}}
        ]
        transcript = {"skills_invoked": ["missing"], "files_read": [".claude/skills/alchemy/SKILL.md", ".claude/skills/alchemy/references/one.md"]}
        filtered = replay.remove_failed_reads(transcript, "\n".join(json.dumps(event) for event in events), self.root)
        self.assertEqual(filtered["skills_invoked"], [])
        self.assertEqual(filtered["files_read"], [".claude/skills/alchemy/references/one.md"])
        self.assertEqual(len(filtered["failed_guidance_loads"]), 2)

    def test_required_core_route_cannot_be_replaced_by_companion(self):
        worth = "functionality-complexity-tradeoff"
        expectation = {"check": "route_includes", "skills": [worth]}
        transcript = {"skills_invoked": [worth], "files_read": [], "paths_searched": []}
        for output in (f"Dispatch: DIRECT\nCompanions: {worth}",
                       f"Core route: None; Companions: {worth}",
                       f"Core route: None; **Companions** — {worth}"):
            with self.subTest(output=output):
                transcript["output"] = output
                self.assertIn(worth, replay.validator.scenario_route(output))
                self.assertNotIn(worth, replay.validator.scenario_core_route(output))
                self.assertFalse(replay.validator.scenario_passes(expectation, transcript))
        for route in ("M", worth, f"M ({worth})"):
            transcript["output"] = f"Core route: {route}; Companions: None"
            self.assertTrue(replay.validator.scenario_passes(expectation, transcript))

    def test_failed_load_with_unresolved_retry_remains_conservative(self):
        body = ".claude/skills/alchemy/SKILL.md"
        for tool in ("Skill", "Read"):
            with self.subTest(tool=tool):
                arguments = {"skill": "alchemy"} if tool == "Skill" else {"file_path": str(self.after / body)}
                events = [
                    {"type": "assistant", "message": {"content": [
                        {"type": "tool_use", "id": "failed", "name": tool, "input": arguments},
                        {"type": "tool_use", "id": "unresolved", "name": tool, "input": arguments},
                        {"type": "text", "text": "Core route: alchemy"}]}},
                    {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "failed", "is_error": True}]}},
                    {"type": "result", "num_turns": 1}]
                def reduce_events():
                    record, reason = replay.validator.scenario_transcript(self.directory, self.scenario, "\n".join(json.dumps(event) for event in events), self.after, revision="captured-source")
                    self.assertEqual(reason, "")
                    return record
                record = reduce_events()
                self.assertEqual(replay.validator.scenario_loaded(record), {"alchemy"})
                self.assertEqual(replay.loaded_guidance(record, {"CLAUDE.md": 10, "alchemy/SKILL.md": 20})["loaded_guidance_words_estimate"], 30)
                events[-1:-1] = [{"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "unresolved", "is_error": True}]}}]
                self.assertEqual(replay.validator.scenario_loaded(reduce_events()), set())

    def test_standard_recording_rejects_failed_body_load_and_accepts_retry(self):
        body = ".claude/skills/alchemy/SKILL.md"
        reference = ".claude/skills/alchemy/references/one.md"
        for tool in ("Skill", "Read"):
            with self.subTest(tool=tool):
                arguments = {"skill": "alchemy"} if tool == "Skill" else {"file_path": str(self.after / body)}
                calls = [
                    {"type": "tool_use", "id": "body-failed", "name": tool, "input": arguments},
                    {"type": "tool_use", "id": "reference-failed", "name": "Read", "input": {"file_path": str(self.after / reference)}}]
                events = [
                    {"type": "assistant", "message": {"content": calls + [{"type": "text", "text": "Core route: alchemy"}]}},
                    {"type": "user", "message": {"content": [
                        {"type": "tool_result", "tool_use_id": "body-failed", "is_error": True},
                        {"type": "tool_result", "tool_use_id": "reference-failed", "is_error": True}]}},
                    {"type": "result", "num_turns": 1}]
                def reduce_events():
                    stream = "\n".join(json.dumps(event) for event in events)
                    record, reason = replay.validator.scenario_transcript(self.directory, self.scenario, stream, self.after, revision="captured-source")
                    self.assertEqual(reason, "")
                    return record
                record = reduce_events()
                self.assertEqual(replay.validator.scenario_loaded(record), set())
                self.assertFalse(replay.validator.scenario_route_loaded(record))
                self.assertTrue(replay.validator.scenario_passes({"check": "file_not_read", "path": reference}, record))
                self.assertEqual(replay.loaded_guidance(record, {"CLAUDE.md": 10, "alchemy/SKILL.md": 20, "alchemy/references/one.md": 30})["loaded_guidance_words_estimate"], 10)
                events[-1:-1] = [
                    {"type": "assistant", "message": {"content": [
                        {**calls[0], "id": "body-success"}, {**calls[1], "id": "reference-success"}]}},
                    {"type": "user", "message": {"content": [
                        {"type": "tool_result", "tool_use_id": "body-success", "is_error": False},
                        {"type": "tool_result", "tool_use_id": "reference-success", "is_error": False}]}}]
                record = reduce_events()
                self.assertEqual(replay.validator.scenario_loaded(record), {"alchemy"})
                self.assertTrue(replay.validator.scenario_route_loaded(record))
                self.assertTrue(replay.validator.scenario_passes({"check": "file_read", "path": reference}, record))
                self.assertEqual(record["failed_guidance_loads"], [])
                self.assertEqual(replay.loaded_guidance(record, {"CLAUDE.md": 10, "alchemy/SKILL.md": 20, "alchemy/references/one.md": 30})["loaded_guidance_words_estimate"], 60)

    def test_content_grep_path_mentions_do_not_load_the_mentioned_body(self):
        mentioned = ".claude/skills/alchemy/SKILL.md"
        reference = ".claude/skills/alchemy/references/one.md"
        for target in (self.after, self.after / "CLAUDE.md"):
            with self.subTest(target=target):
                events = [
                    {"message": {"content": [{"type": "tool_use", "id": "mention", "name": "Grep", "input": {"path": str(target), "output_mode": "content"}}]}},
                    {"message": {"content": [{"type": "tool_result", "tool_use_id": "mention", "content":
                        f"CLAUDE.md:14:use {mentioned}\ndocs/design.md-15-see {self.after / reference}"}]}}]
                reads = replay.grep_guidance_reads("\n".join(json.dumps(event) for event in events), self.after)
                self.assertEqual(reads, [])
                record = {"skills_invoked": [], "files_read": [], "paths_searched": [], "guidance_content_reads": reads, "output": "Core route: alchemy"}
                self.assertEqual(replay.validator.scenario_loaded(record), set())
                self.assertFalse(replay.validator.scenario_route_loaded(record))
                self.assertTrue(replay.validator.scenario_passes({"check": "file_not_read", "path": reference}, record))

    def test_content_grep_accepts_actual_absolute_filename_prefixes(self):
        for namespace in ("claude", "agents"):
            for delimiter in (":12:", "-13-"):
                with self.subTest(namespace=namespace, delimiter=delimiter):
                    filename = f".{namespace}/skills/alchemy/SKILL.md"
                    events = [
                        {"message": {"content": [{"type": "tool_use", "id": "absolute", "name": "Grep", "input": {"path": str(self.after), "output_mode": "content"}}]}},
                        {"message": {"content": [{"type": "tool_result", "tool_use_id": "absolute", "content":
                            f"C:/projects/Skills Library/{filename}{delimiter}actual body content"}]}}]
                    self.assertEqual(replay.grep_guidance_reads("\n".join(json.dumps(event) for event in events), self.after), [filename])

    def test_product_provenance_is_anonymous_and_omits_guidance_and_outside_access(self):
        events = [
            {"message": {"content": [
                {"type": "tool_use", "id": "skill", "name": "Skill", "input": {"skill": "alchemy"}},
                {"type": "tool_use", "id": "guidance-read", "name": "Read", "input": {"file_path": str(self.root / ".claude" / "skills" / "alchemy" / "SKILL.md")}},
                {"type": "tool_use", "id": "guidance-search", "name": "Grep", "input": {"path": str(self.root / ".claude"), "pattern": "secret"}},
                {"type": "tool_use", "id": "outside", "name": "Read", "input": {"file_path": str(self.root.parent / "outside.txt")}},
                {"type": "tool_use", "id": "product", "name": "Grep", "input": {"path": str(self.root), "pattern": "color", "output_mode": "content"}},
                {"type": "tool_use", "id": "glob", "name": "Glob", "input": {"pattern": "**/*.css"}}]}},
            {"message": {"content": [
                {"type": "tool_result", "tool_use_id": "skill", "content": "secret source body"},
                {"type": "tool_result", "tool_use_id": "guidance-read", "content": "secret source body"},
                {"type": "tool_result", "tool_use_id": "guidance-search", "content": "secret source body"},
                {"type": "tool_result", "tool_use_id": "outside", "content": "secret outside body"},
                {"type": "tool_result", "tool_use_id": "product", "content": ".claude\\skills\\alchemy\\SKILL.md:20:secret source body\n" + str(self.root / "src" / "style.css") + ":10:color: red"},
                {"type": "tool_result", "tool_use_id": "glob", "content": "No files found"}]}}
        ]
        transcript = {"files_read": [".claude/skills/alchemy/SKILL.md", "<outside project>", "src/style.css"], "paths_searched": [".claude/skills", ".", "<outside project>"]}
        provenance = replay.product_provenance(transcript, "\n".join(json.dumps(event) for event in events), self.root)
        serialized = json.dumps(provenance)
        self.assertNotIn("secret", serialized)
        self.assertNotIn(str(self.root), serialized)
        self.assertNotIn(".claude", serialized)
        self.assertNotIn("outside.txt", serialized)
        self.assertEqual(provenance["files_read"], ["src/style.css"])
        self.assertEqual(provenance["paths_searched"], ["."])
        self.assertEqual(len(provenance["observations"]), 2)
        self.assertTrue(provenance["observations"][0]["guidance_output_omitted"])
        self.assertIn("color: red", provenance["observations"][0]["result"])
        self.assertEqual(provenance["observations"][1]["result"], "No files found")
        context = {"request": "request", "product_fixture": {}, "product_tool_provenance": {"A": provenance, "B": provenance}}
        prompt = replay.judge_prompt({"A": "report one", "B": "report two"}, ["criterion"], context)
        self.assertNotIn("before", prompt)
        self.assertNotIn("after", prompt)
        self.assertIn("does not make an executed search fabricated", prompt)
        bounded = replay.product_provenance(transcript, "\n".join(json.dumps(event) for event in events), self.root, limit=1)
        self.assertEqual(bounded["observations"], [])
        self.assertEqual(bounded["omitted_observations"], 2)

    def test_content_grep_loads_guidance_once_and_checker_treats_it_as_read(self):
        body = ".claude/skills/alchemy/SKILL.md"
        guide = ".claude/skills/alchemy/references/operating-guide.md"
        empty = ".claude/skills/alchemy/references/empty.md"
        discovery = ".claude/skills/alchemy/references/discovery.md"
        errored = ".claude/skills/alchemy/references/errored.md"
        events = [
            {"message": {"content": [
                {"type": "tool_use", "id": "root", "name": "Grep", "input": {"path": str(self.after), "output_mode": "content"}},
                {"type": "tool_use", "id": "single", "name": "Grep", "input": {"path": str(self.after / guide), "output_mode": "content", "-n": False}},
                {"type": "tool_use", "id": "empty", "name": "Grep", "input": {"path": str(self.after / empty), "output_mode": "content"}},
                {"type": "tool_use", "id": "discovery", "name": "Grep", "input": {"output_mode": "files_with_matches"}},
                {"type": "tool_use", "id": "error", "name": "Grep", "input": {"output_mode": "content"}}]}},
            {"message": {"content": [
                {"type": "tool_result", "tool_use_id": "root", "content": body.replace("/", "\\") + ":12:dispatch\n" + body + "-13-more context\n" + guide + ":4:adaptive rules"},
                {"type": "tool_result", "tool_use_id": "single", "content": [{"type": "text", "text": "adaptive rules without line numbers"}]},
                {"type": "tool_result", "tool_use_id": "empty", "content": "No matches found"},
                {"type": "tool_result", "tool_use_id": "discovery", "content": discovery},
                {"type": "tool_result", "tool_use_id": "error", "is_error": True, "content": errored + ":4:rules"}]}}
        ]
        reads = replay.grep_guidance_reads("\n".join(json.dumps(event) for event in events), self.after)
        self.assertEqual(reads, sorted([body, guide]))
        transcript = {"skills_invoked": ["alchemy"], "files_read": [body], "paths_searched": [],
                      "guidance_content_reads": reads, "output": "Core route: alchemy"}
        counts = {"CLAUDE.md": 10, "alchemy/SKILL.md": 20, "alchemy/references/operating-guide.md": 30}
        self.assertEqual(replay.loaded_guidance(transcript, counts)["loaded_guidance_words_estimate"], 60)
        self.assertFalse(replay.validator.scenario_passes({"check": "file_not_read", "path": guide}, transcript))
        self.assertTrue(replay.validator.scenario_passes({"check": "file_read", "path": guide}, transcript))
        transcript.update(skills_invoked=[], files_read=[])
        self.assertEqual(replay.validator.scenario_loaded(transcript), {"alchemy"})
        self.assertTrue(replay.validator.scenario_route_loaded(transcript))

    def test_interrupted_judge_preserves_attempt_and_resume_reuses_completed_arms(self):
        artifact = self.freeze()
        interrupted = False
        def interrupted_judge(command, cwd, stdout, stderr, timeout, stdin=None):
            nonlocal interrupted
            if "--safe-mode" in command and not interrupted:
                interrupted = True
                stdout.write_text("partial judge response", encoding="utf-8")
                stderr.write_text("", encoding="utf-8")
                raise KeyboardInterrupt()
            return self.cli(command, cwd, stdout, stderr, timeout, stdin=stdin)
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=interrupted_judge):
            self.assertEqual(replay.execute(artifact, self.destination), 130)
        saved = json.loads(self.destination.read_text(encoding="utf-8"))
        self.assertEqual(saved["completed_pairs"], 1)
        first_attempt = saved["runs"][0]["judge_attempts"][0]
        self.assertEqual(first_attempt["status"], "interrupted")
        self.assertIn("partial judge", (self.destination.parent / first_attempt["stdout_file"]).read_text(encoding="utf-8"))
        self.calls.clear()
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=self.cli):
            self.assertEqual(replay.main(["--resume", str(self.destination)]), 0)
        self.assertEqual(len([call for call in self.calls if call[0] == "arm"]), 4)
        resumed = json.loads(self.destination.read_text(encoding="utf-8"))
        attempts = resumed["runs"][0]["judge_attempts"]
        self.assertEqual([attempt["status"] for attempt in attempts], ["interrupted", "complete"])
        self.assertNotEqual(attempts[0]["stdout_file"], attempts[1]["stdout_file"])
        self.assertIn("partial judge", (self.destination.parent / attempts[0]["stdout_file"]).read_text(encoding="utf-8"))

    def test_malformed_judge_output_is_failure_and_resume_only_retries_judges(self):
        artifact = self.freeze()
        def malformed_cli(command, cwd, stdout, stderr, timeout, stdin=None):
            if "--safe-mode" in command:
                stdout.write_text("Unable to evaluate these reports.", encoding="utf-8")
                stderr.write_text("", encoding="utf-8")
                return 0, None
            return self.cli(command, cwd, stdout, stderr, timeout, stdin=stdin)
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=malformed_cli):
            self.assertEqual(replay.execute(artifact, self.destination), 1)
        self.assertEqual(artifact["completed_pairs"], 3)
        self.assertEqual(artifact["status"], "incomplete")
        for pair in artifact["runs"]:
            self.assertNotIn("blind_judge", pair)
            self.assertIn("valid JSON", pair["blind_judge_error"])
            self.assertEqual(pair["judge_attempts"][0]["status"], "error")
        self.calls.clear()
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=self.cli):
            self.assertEqual(replay.execute(artifact, self.destination), 0)
        self.assertFalse([call for call in self.calls if call[0] == "arm"])
        self.assertEqual(len([call for call in self.calls if call[0] == "judge"]), 3)
        for pair in artifact["runs"]:
            attempt = pair["judge_attempts"][0]
            self.assertIn("Unable to evaluate", (self.destination.parent / attempt["stdout_file"]).read_text(encoding="utf-8"))

    def test_judge_json_contract_and_large_stdin_prompt(self):
        valid = {"A": {"c1": "pass"}, "B": {"c1": "pass"}, "preference": "tie", "reason": "Both satisfy the criterion."}
        self.assertEqual(replay.parse_judge_result("```json\n" + json.dumps(valid) + "\n```"), valid)
        for invalid in ("", "not JSON", "{}", "[]", json.dumps({**valid, "preference": "candidate"}), json.dumps({**valid, "reason": " "}), json.dumps({**valid, "A": {}}), json.dumps(valid) + " commentary"):
            with self.subTest(response=invalid), self.assertRaises(RuntimeError):
                replay.parse_judge_result(invalid)
        observed = []
        def large_cli(command, cwd, stdout, stderr, timeout, stdin=None):
            self.assertLess(sum(len(part) for part in command), 2000)
            self.assertGreater(len(stdin), 200000)
            self.assertEqual(list(cwd.iterdir()), [])
            observed.append(stdin)
            stdout.write_text(json.dumps(valid), encoding="utf-8")
            stderr.write_text("", encoding="utf-8")
            return 0, None
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=large_cli):
            result = replay.judge_pair({"A": "report A", "B": "report B"}, ["criterion"], {"product_fixture": "x" * 210000}, None, self.root / "large-judge", 30)
        self.assertEqual(json.loads(result), valid)
        self.assertEqual(len(observed), 1)
        stdout, stderr = self.root / "stdin.stdout", self.root / "stdin.stderr"
        code, error = replay.capture([sys.executable, "-c", "import sys; print(len(sys.stdin.buffer.read()))"], self.root, stdout, stderr, 10, stdin=b"x" * 210000)
        self.assertEqual(code, 0)
        self.assertIsNone(error)
        self.assertEqual(stdout.read_text(encoding="utf-8").strip(), "210000")

    def test_cleanup_locks_do_not_discard_completed_results_and_are_reported(self):
        artifact = self.freeze()
        actual_remove = replay.shutil.rmtree
        locked_project = None
        failed = 0
        def locked_remove(path, *args, **kwargs):
            nonlocal locked_project, failed
            if locked_project is None:
                locked_project = Path(path)
            if Path(path) == locked_project and failed < 3:
                failed += 1
                raise PermissionError("simulated temporary directory lock")
            return actual_remove(path, *args, **kwargs)
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=self.cli), patch.object(replay.shutil, "rmtree", side_effect=locked_remove), patch.object(replay.time, "sleep"):
            self.assertEqual(replay.execute(artifact, self.destination), 0)
        first = artifact["runs"][0]["arms"][artifact["runs"][0]["arm_order"][0]]
        self.assertEqual(first["status"], "complete")
        self.assertEqual(first["expectations_passed"], 1)
        self.assertIn("after 3 attempts", first["cleanup_warnings"][0])
        self.assertEqual(failed, 3)
        self.assertEqual(replay.cleanup_workspace(locked_project), [])
        self.assertTrue(replay.cleanup_workspace(self.root / "not-allocated"))

    def test_resume_recovers_cleanup_only_error_from_completed_raw_trace(self):
        artifact = self.freeze()
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=self.cli):
            self.assertEqual(replay.execute(artifact, self.destination), 0)
        previous = artifact["runs"][0]["arms"]["before"]
        original_words = previous["word_count"]
        original_output = previous["transcript"]["output"]
        previous["status"] = "error"
        previous["error"] = "[WinError 32] process locked temporary workspace l-gevity-replay-original"
        previous.pop("transcript")
        artifact["runs"][0]["status"] = "incomplete"
        artifact["runs"][0].pop("blind_judge")
        artifact["completed_pairs"] = 2
        self.calls.clear()
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=self.cli):
            self.assertEqual(replay.execute(artifact, self.destination), 0)
        recovered = artifact["runs"][0]["arms"]["before"]
        self.assertEqual(recovered["status"], "complete")
        self.assertTrue(recovered["recovered_from_completed_trace"])
        self.assertEqual(recovered["word_count"], original_words)
        self.assertEqual(recovered["transcript"]["output"], original_output)
        self.assertIn("WinError 32", recovered["cleanup_warnings"][0])
        self.assertEqual(recovered["previous_attempts"][-1]["status"], "error")
        self.assertIn("WinError 32", recovered["previous_attempts"][-1]["error"])
        self.assertFalse([call for call in self.calls if call[0] == "arm"])
        self.assertEqual(len([call for call in self.calls if call[0] == "judge"]), 1)

    def test_standard_revision_covers_unnamed_siblings_references_and_criteria(self):
        sibling = self.after / ".claude" / "skills" / "unnamed-sibling"
        (sibling / "references").mkdir(parents=True)
        (sibling / "SKILL.md").write_text("sibling guidance", encoding="utf-8")
        reference = sibling / "references" / "rules.md"
        reference.write_text("original sibling rule", encoding="utf-8")
        with patch.object(replay.validator, "ROOT", self.after):
            original = replay.validator.scenario_revision(self.directory, self.scenario)
            reference.write_text("changed sibling rule", encoding="utf-8")
            self.assertNotEqual(replay.validator.scenario_revision(self.directory, self.scenario), original)
            reference.write_text("original sibling rule", encoding="utf-8")
            self.assertEqual(replay.validator.scenario_revision(self.directory, self.scenario), original)
            changed_criteria = json.loads(json.dumps(self.scenario))
            changed_criteria["expect"][0]["values"].append("DIRECT")
            self.assertNotEqual(replay.validator.scenario_revision(self.directory, changed_criteria), original)
            changed_rubric = json.loads(json.dumps(self.scenario))
            changed_rubric["blind_judge_rubric"].append("Another predeclared obligation")
            self.assertNotEqual(replay.validator.scenario_revision(self.directory, changed_rubric), original)

    def test_standard_captured_revision_ignores_later_root_and_fixture_changes(self):
        captured = self.root / "captured-project"
        replay.shutil.copytree(self.after, captured)
        replay.shutil.copytree(self.directory / "project", captured, dirs_exist_ok=True)
        with patch.object(replay.validator, "ROOT", self.after):
            original = replay.validator.scenario_revision(self.directory, self.scenario)
            self.assertEqual(replay.validator.scenario_revision(self.directory, self.scenario, source_root=captured), original)
            (self.after / "CLAUDE.md").write_text("changed live root", encoding="utf-8")
            (self.after / ".claude" / "skills" / "alchemy" / "SKILL.md").write_text("changed live body", encoding="utf-8")
            (self.directory / "project" / "input.txt").unlink()
            (self.directory / "project" / "new-file.txt").write_text("added later", encoding="utf-8")
            self.assertEqual(replay.validator.scenario_revision(self.directory, self.scenario, source_root=captured), original)
            self.assertNotEqual(replay.validator.scenario_revision(self.directory, self.scenario), original)
            stream = "\n".join(json.dumps(event) for event in [
                {"type": "assistant", "message": {"content": [{"type": "text", "text": "Decision: SKIP"}]}},
                {"type": "result", "is_error": False, "num_turns": 1}])
            with patch.object(replay.validator, "scenario_revision", side_effect=AssertionError("must not retrostamp from live source")):
                transcript, reason = replay.validator.scenario_transcript(self.directory, self.scenario, stream, captured, revision=original)
            self.assertEqual(reason, "")
            self.assertEqual(transcript["revision"], original)

    def test_standard_recorder_captures_revision_before_model_call(self):
        with patch.object(replay.validator, "ROOT", self.after):
            original = replay.validator.scenario_revision(self.directory, self.scenario)
        def model(command, **kwargs):
            self.assertEqual((kwargs["cwd"] / "input.txt").read_text(encoding="utf-8"), "identical fixture")
            (self.after / "CLAUDE.md").write_text("live guide changed during model call", encoding="utf-8")
            (self.directory / "project" / "input.txt").unlink()
            (self.directory / "project" / "added-later.txt").write_text("new live fixture file", encoding="utf-8")
            stream = "\n".join(json.dumps(event) for event in [
                {"type": "assistant", "message": {"content": [{"type": "text", "text": "Decision: SKIP"}]}},
                {"type": "result", "is_error": False, "num_turns": 1}])
            return subprocess.CompletedProcess(command, 0, stdout=stream.encode("utf-8"), stderr=b"")
        with patch.object(replay.validator, "ROOT", self.after), patch.object(replay.validator, "CLAUDE_SKILLS", self.after / ".claude" / "skills"), patch.object(replay.validator, "SCENARIOS", self.root / ".scenarios"), patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay.subprocess, "run", side_effect=model):
            self.assertEqual(replay.validator.record_scenarios(["case"]), 0)
        transcript = json.loads((self.directory / "transcript.json").read_text(encoding="utf-8"))
        self.assertEqual(transcript["revision"], original)

    def test_frozen_parser_accounting_hashes_and_resume_version_notice(self):
        artifact = self.freeze()
        self.assertEqual(artifact["accounting_runtime_sha256"], replay.accounting_runtime_hash())
        self.assertEqual(len(artifact["runner_source_sha256"]), 64)
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=self.cli), patch.object(replay.validator, "scenario_guidance_content_reads", side_effect=AssertionError("live parser must not replace frozen checker")), patch.object(replay.validator, "scenario_filter_failed_loads", side_effect=AssertionError("live filter must not replace frozen checker")):
            self.assertEqual(replay.execute(artifact, self.destination), 0)
        original_estimates = []
        for pair in artifact["runs"]:
            for arm in ("before", "after"):
                result = pair["arms"][arm]
                original_estimates.append(result["loaded_guidance_words_estimate"])
                provenance = result["accounting_provenance"]
                self.assertEqual(provenance["parser_origin"], "frozen-checker")
                self.assertEqual(provenance["load_filter_origin"], "frozen-checker")
                self.assertEqual(provenance["runtime_sha256"], artifact["accounting_runtime_sha256"])
                self.assertEqual(provenance["checker_sha256"], artifact["checker_sha256"])
        self.calls.clear()
        with patch.object(replay, "accounting_runtime_hash", return_value="f" * 64), patch.object(replay, "capture", side_effect=AssertionError("completed estimates must not rerun")):
            self.assertEqual(replay.execute(artifact, self.destination), 0)
        self.assertIn("accounting_change_notice", artifact)
        self.assertEqual(len(artifact["execution_versions"]), 2)
        self.assertEqual(artifact["execution_versions"][-1]["accounting_runtime_sha256"], "f" * 64)
        self.assertEqual([pair["arms"][arm]["loaded_guidance_words_estimate"] for pair in artifact["runs"] for arm in ("before", "after")], original_estimates)


    def test_record_sink_scoped_permission_persistence_and_anonymous_judging(self):
        self.args.decision_records = True
        self.args.runs = 1
        artifact = self.freeze()
        def with_record(command, cwd, stdout, stderr, timeout, stdin=None):
            if "--safe-mode" not in command:
                self.assertIn("Write", command[command.index("--tools") + 1].split(","))
                allowed = command[command.index("--allowedTools") + 1].split(",")
                self.assertIn("Edit(/.decision-record.md)", allowed)
                self.assertNotIn("Write", allowed)
                self.assertNotIn("Edit", allowed)
                self.assertEqual(command[command.index("--permission-mode") + 1], "dontAsk")
                (cwd / ".decision-record.md").write_text(f"Complete record for {cwd}: " + "evidence " * 500, encoding="utf-8")
            else:
                packet = stdin.decode("utf-8")
                self.assertIn("Complete record for .:", packet)
                self.assertNotIn(".decision-record.md", packet)
                self.assertNotIn("log_file", packet)
            return self.cli(command, cwd, stdout, stderr, timeout, stdin)
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=with_record):
            self.assertEqual(replay.execute(artifact, self.destination), 0)
        for arm in ("before", "after"):
            result = artifact["runs"][0]["arms"][arm]
            self.assertEqual(result["word_count"], 12)
            record = result["decision_record"]
            self.assertEqual(record["sha256"], replay.hashlib.sha256(record["text"].encode()).hexdigest())
            self.assertTrue((self.destination.with_suffix(".logs") / record["log_file"]).is_file())
        self.assertEqual(artifact["record_sink_context"], replay.RECORD_SINK_CONTEXT)
        artifact["record_sink_context"] += " changed"
        with self.assertRaisesRegex(ValueError, "record-sink context"):
            replay.execute(artifact, self.destination)

    def test_record_sink_does_not_make_mutated_inputs_successful(self):
        self.args.decision_records = True
        self.args.runs = 1
        artifact = self.freeze()
        def mutate(command, cwd, stdout, stderr, timeout, stdin=None):
            result = self.cli(command, cwd, stdout, stderr, timeout, stdin)
            if "--safe-mode" not in command:
                (cwd / "input.txt").write_text("illegal mutation", encoding="utf-8")
            return result
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=mutate):
            self.assertEqual(replay.execute(artifact, self.destination), 1)
        for result in artifact["runs"][0]["arms"].values():
            self.assertEqual(result["status"], "error")
            self.assertIn("input.txt", result["changed_inputs"])

    def test_interrupted_record_sink_keeps_record_log(self):
        self.args.decision_records = True
        self.args.runs = 1
        artifact = self.freeze()
        def interrupt(command, cwd, stdout, stderr, timeout, stdin=None):
            (cwd / ".decision-record.md").write_text("Incomplete but preserved", encoding="utf-8")
            raise KeyboardInterrupt
        with patch.object(replay.shutil, "which", return_value="mock-claude"), patch.object(replay, "capture", side_effect=interrupt):
            self.assertEqual(replay.execute(artifact, self.destination), 130)
        records = list(self.destination.with_suffix(".logs").glob("*.decision-record.md"))
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].read_text(encoding="utf-8"), "Incomplete but preserved")


if __name__ == "__main__":
    unittest.main()
