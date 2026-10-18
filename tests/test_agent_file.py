"""An arm's stage that runs as a Symphony agent file (flowbench/agent_file.py)."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flowbench import agent_file, run  # noqa: E402

AGENT = """---
name: reviewer
description: Reviews one change.
tools: Read, Grep, Bash(git:*)
model: opus
---

Review the change.
"""


class AgentFile(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)

    def test_read_and_write_a_definition_without_the_model(self):
        (self.dir / "a.md").write_text(AGENT)
        agent = agent_file.read(self.dir / "a.md")
        path, name = agent_file.write_definition(agent, self.dir / "a.json")
        self.assertEqual(name, "reviewer")
        definition = json.loads(path.read_text())["reviewer"]
        self.assertEqual(definition["tools"], ["Read", "Grep", "Bash(git:*)"])
        self.assertNotIn("model", definition)

    def test_a_file_without_front_matter_is_refused(self):
        (self.dir / "a.md").write_text("Review the change.\n")
        with self.assertRaises(agent_file.AgentFileError):
            agent_file.read(self.dir / "a.md")

    def test_the_command_runs_as_the_agent_under_the_runs_model_and_denials(self):
        command = run.claude_command("claude-sonnet-5-5", "high", 50, run.DISALLOWED_TOOLS, "m", agent=("/r/a.json", "reviewer"))
        self.assertEqual(command[-4:], ["--agents", "/r/a.json", "--agent", "reviewer"])
        self.assertIn("--disallowedTools", command)
        self.assertEqual(command[command.index("--model") + 1], "claude-sonnet-5-5")

    def test_an_arm_naming_an_agent_loads_it(self):
        arm = self.dir / "arm"
        shutil.copytree(run.ARMS_DIR / "solo", arm)
        (arm / "agents").mkdir()
        (arm / "agents" / "reviewer.md").write_text(AGENT)
        config = json.loads((arm / "stages.json").read_text())
        config["stages"][0]["agent"] = "agents/reviewer.md"
        (arm / "stages.json").write_text(json.dumps(config))
        self.assertEqual(run.load_arm(arm)["stages"][0]["agent_definition"]["name"], "reviewer")
        config["stages"][0]["agent"] = "agents/missing.md"
        (arm / "stages.json").write_text(json.dumps(config))
        with self.assertRaisesRegex(run.RunError, "agent"):
            run.load_arm(arm)


if __name__ == "__main__":
    unittest.main()
