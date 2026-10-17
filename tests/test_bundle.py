"""bundle.py keeps counts, verdicts and the patch, and drops the agents'
words and the host's paths."""

import json
import tempfile
import unittest
from pathlib import Path

from flowbench import bundle, record


class Bundle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.run = self.root / "logs" / "pilot" / "solo" / "x__y-1" / "attempt-1"
        (self.run / "agents").mkdir(parents=True)
        record.write_json(self.run / "result.json", {
            "agents": [{"agent": "work", "result_text": "the agent's words", "tokens": {"output": 3}}],
            "scoring": {"resolved": True, "run_id": "rid", "command": ["/home/h/swebench", "eval"],
                        "report": "score/r.json", "instance_log": "score/run.log"},
            "flow": {"merges": {"notes": "the merger's words", "tests": "passed"}},
            "workspace": "/tmp/flowbench-ws", "instance": "x__y-1"})
        (self.run / "prediction.jsonl").write_text('{"model_patch": "diff"}\n', encoding="utf-8")
        (self.run / "events.jsonl").write_text('{"kind": "prepared"}\n', encoding="utf-8")
        record.write_json(self.run / "audit.json", {"excluded": False, "network_commands": ["cd /home/x && pip install y"]})
        (self.run / "agents" / "work.prompt.md").write_text("run token flowbench-abc", encoding="utf-8")
        stream = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash"},
                                                                {"type": "text", "text": "hi"}]}},
                  {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash"}]}}]
        (self.run / "agents" / "work.stream.jsonl").write_text(
            "".join(json.dumps(line) + "\n" for line in stream) + "not json\n", encoding="utf-8")
        report = self.run / "score" / "logs" / "run_evaluation" / "rid" / "model" / "x__y-1" / "report.json"
        report.parent.mkdir(parents=True)
        record.write_json(report, {"x__y-1": {"resolved": True}})
        other = self.run / "score" / "logs" / "run_evaluation" / "older" / "model" / "x__y-1" / "report.json"
        other.parent.mkdir(parents=True)
        record.write_json(other, {"x__y-1": {"resolved": False}})

    def tearDown(self):
        self.temp.cleanup()

    def test_the_bundle_keeps_the_verdict_and_drops_text_and_paths(self):
        done = bundle.bundle(self.root / "logs", "pilot", self.root / "out")
        self.assertEqual(done, ["solo/x__y-1/attempt-1"])
        out = self.root / "out" / "solo" / "x__y-1" / "attempt-1"
        result = record.read_json(out / "result.json")
        self.assertEqual(result["scoring"], {"resolved": True, "run_id": "rid"})
        self.assertEqual(result["flow"], {"merges": {"tests": "passed"}})
        self.assertEqual(result["workspace"], "<path>")
        self.assertEqual(record.read_json(out / "audit.json")["network_commands"], ["cd <path> && pip install y"])
        self.assertNotIn("result_text", result["agents"][0])
        self.assertEqual(result["agents"][0]["tokens"], {"output": 3})
        self.assertEqual(record.read_json(out / "tools.json"), {"work": {"Bash": 2}})
        self.assertEqual(record.read_json(out / "report.json"), {"x__y-1": {"resolved": True}})
        self.assertTrue((out / "prediction.jsonl").is_file())
        self.assertFalse(any("prompt" in path.name or "stream" in path.name for path in out.iterdir()))
        self.assertNotIn("flowbench-abc", "".join(path.read_text() for path in out.iterdir()))

    def test_a_second_bundle_leaves_nothing_of_the_first(self):
        stale = self.root / "out" / "solo" / "x__y-1" / "attempt-1" / "stale.json"
        stale.parent.mkdir(parents=True)
        stale.write_text("{}", encoding="utf-8")
        bundle.bundle(self.root / "logs", "pilot", self.root / "out")
        self.assertFalse(stale.exists())


if __name__ == "__main__":
    unittest.main()
