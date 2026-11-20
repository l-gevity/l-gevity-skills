"""Regression checks for scheduling, evidence reuse, and scenario measurements."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents/skills/alchemy-orchestrate/scripts"
sys.path.insert(0, str(SCRIPTS))
import check_orchestration as checker
import record_evidence as recorder


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Scheduling(unittest.TestCase):
    def setUp(self):
        self.packages = {
            "A": {"owner": "alice", "depends_on": []},
            "B": {"owner": "bob", "depends_on": []},
            "C": {"owner": "carol", "depends_on": ["A"]},
        }

    def ready(self, completed=(), running=(), cap=2):
        return checker.ready_packages(self.packages, completed, running, cap, "lead")

    def test_release_dependent_while_unrelated_package_runs(self):
        self.assertEqual(self.ready(["A"], ["B"]), ["C"])

    def test_capacity_and_dependencies(self):
        self.assertEqual(self.ready(), ["A", "B"])
        self.assertEqual(self.ready(running=["A", "B"]), [])
        self.assertEqual(self.ready(running=["A"], cap=1), [])
        self.assertEqual(self.ready(["A", "B", "C"]), [])
        with self.assertRaises(checker.InputError):
            self.ready(running=["A", "B"], cap=1)

    def test_ready_schedule_removes_unrelated_wave_wait(self):
        durations = {"A": 1, "B": 10, "C": 10}
        now, done, active = 0, [], {}
        while len(done) < len(self.packages):
            for pid in self.ready(done, list(active)):
                active[pid] = now + durations[pid]
            now = min(active.values())
            finished = [pid for pid, end in active.items() if end == now]
            done.extend(finished)
            for pid in finished:
                del active[pid]
        self.assertEqual(now, 11)  # Wave barriers take max(1, 10) + 10 = 20.

    def test_lead_is_excluded_from_subagent_cap(self):
        self.packages["A"]["owner"] = "lead"
        self.assertEqual(self.ready(running=["B"], cap=1), ["A"])

    def test_reject_impossible_runtime_state(self):
        for done, active in ((["missing"], []), (["C"], []), ([], ["C"]), (["A"], ["A"])):
            with self.subTest(done=done, active=active), self.assertRaises(checker.InputError):
                self.ready(done, active)

    def test_owner_cannot_execute_two_packages(self):
        self.packages["C"]["owner"] = " BOB "
        self.assertEqual(self.ready(["A"], ["B"]), [])
        self.packages["A"]["owner"] = "bob"
        with self.assertRaises(checker.InputError):
            self.ready(running=["A", "B"])

    def test_failed_plan_releases_nothing(self):
        plan = json.loads((ROOT / ".adversarial/plan-parallel-independent-pass/plan.json").read_text())
        plan["packages"][0]["depends_on"] = ["missing"]
        result = checker.check_plan(plan, checker.load_profile())
        self.assertNotEqual(result["verdict"], "PASS")
        self.assertEqual(result["ready"], [])

    def test_plan_cli_reports_ready_state(self):
        plan = ROOT / ".adversarial/plan-parallel-independent-pass/plan.json"
        run = subprocess.run([sys.executable, str(SCRIPTS / "check_orchestration.py"), "plan", str(plan)],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["ready"], ["P1", "P2"])


class EvidenceReuse(unittest.TestCase):
    def test_opt_in_reuses_execution_but_retains_criterion_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps({"packages": [{"acceptance": [
                {"id": "AC1", "check": "command", "command": "check"},
                {"id": "AC2", "check": "command", "command": "check"},
            ]}]}))
            profile = checker.load_profile()
            profile["repository"]["verification"] = [{"id": "suite", "command": "check"}]
            for reuse, count in ((False, 3), (True, 1)):
                with patch.object(recorder.checker, "_workspace_problems", return_value=([], True)), \
                     patch.object(recorder.checker, "_git", return_value=("abcdef123456", None)), \
                     patch.object(recorder.subprocess, "run", return_value=subprocess.CompletedProcess("check", 7, b"failure")) as run:
                    result = recorder.record(plan_path, root, profile, [], False, root / ".alchemy/runs/evidence", 60,
                                             reuse_identical=reuse)
                self.assertEqual(run.call_count, count)
                self.assertEqual(result["verdict"], "FAIL")
                self.assertEqual([e["id"] for e in result["evidence"]],
                                 ["AC1@abcdef1", "AC2@abcdef1", "suite@abcdef1"])
                self.assertEqual([e["exit_code"] for e in result["evidence"]], [7, 7, 7])
                for entry in result["evidence"]:
                    self.assertEqual((root / entry["log"]).read_bytes(), b"failure")
                    self.assertEqual(json.loads(next((root / '.alchemy/runs/evidence').glob(entry['id'] + '.json')).read_text()), entry)
                if reuse:
                    self.assertEqual(result["evidence"][1]["reused_from"], "AC1@abcdef1")


class Measurements(unittest.TestCase):
    def test_runtime_metrics_are_retained_and_optional(self):
        validator = load("skill_validator", ROOT / "scripts/validate-skills.py")
        directory = ROOT / ".scenarios/dispatch-routine-skip"
        scenario, _ = validator.load_scenario(directory)
        values = {"num_turns": 2, "duration_ms": 1000, "duration_api_ms": 800,
                  "total_cost_usd": 0.02, "usage": {"input_tokens": 30, "output_tokens": 10}}
        stream = json.dumps({"type": "result", **values})
        transcript, reason = validator.scenario_transcript(directory, scenario, stream, ROOT)
        self.assertFalse(reason)
        self.assertEqual(transcript["metrics"], {k: v for k, v in values.items() if k != "num_turns"})
        transcript, _ = validator.scenario_transcript(directory, scenario, '{"type":"result"}', ROOT)
        self.assertEqual(transcript["metrics"], {})

    def test_repository_fixtures_use_bounded_isolated_workers(self):
        validator = load("fixture_validator", ROOT / "scripts/validate-skills.py")
        seen = []
        def run_case(checker, scratch, unowned, raised, cycles, renamed):
            self.assertTrue(scratch.is_dir())
            seen.append(scratch)
            verdict, codes = validator.GATE_REPOSITORY_CASES[(unowned, raised, cycles, renamed)]
            return {"verdict": verdict, "errors": [{"code": code} for code in codes]}
        with patch.object(validator, "gate_repository_report", side_effect=run_case), \
             patch.object(validator, "ThreadPoolExecutor", wraps=validator.ThreadPoolExecutor) as executor:
            validator.validate_gate_repository_rules()
        executor.assert_called_once_with(max_workers=3)
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(len(seen), len(validator.GATE_REPOSITORY_CASES))
        self.assertFalse(any(p.exists() for p in seen))


class ReviewDelta(unittest.TestCase):
    def test_correction_adapter_supplies_delta(self):
        adapter = ROOT / ".agents/skills/alchemy-orchestrate/adapters/unstoppable"
        correction = (adapter / "pipelines/alchemy-multi-agent.yaml").read_text().split("    correction:", 1)[1]
        snapshot_step = correction.split("        - id: snapshot", 1)[1].split("        - id: review", 1)[0]
        self.assertIn("base_ledger: ${{ needs.plan_check.outputs.run_dir }}/ledger.json", snapshot_step)
        self.assertNotIn("base: ${{ needs.plan_check.outputs.base_commit }}", snapshot_step)
        self.assertIn("${{ steps.snapshot.outputs.base_commit }}", correction)

    def test_ledger_selects_prior_head_and_rejects_conflicting_base(self):
        snapshot = load("review_snapshot", ROOT / ".agents/skills/alchemy-orchestrate/adapters/unstoppable/actions/alchemy-snapshot/snapshot.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / "ledger.json"
            ledger.write_text(json.dumps({"schema": "alchemy-ledger/1", "head_commit": "abcdef1"}))
            self.assertEqual(snapshot.review_base(root, "", str(ledger)), "abcdef1")
            with self.assertRaises(snapshot.InputError):
                snapshot.review_base(root, "123abcd", str(ledger))
            ledger.write_text('{"schema":"alchemy-ledger/1","head_commit":"--all"}')
            with self.assertRaises(snapshot.InputError):
                snapshot.review_base(root, "", str(ledger))


if __name__ == "__main__":
    unittest.main()
