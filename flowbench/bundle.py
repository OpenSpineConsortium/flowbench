"""The committed record of a tag's runs: what a reader needs to check the
report, and nothing the host alone should keep.

For each run directory under LOGS/TAG/<arm>/<instance>/attempt-N, the
bundle writes OUT/<arm>/<instance>/attempt-N with result.json less every
agent's text and every host path, prediction.jsonl (the patch the scorer
took), events.jsonl, audit.json, the harness's per-instance report.json
(the tests it ran and their verdicts), and tools.json, the count of each
tool every agent called, read from its stream, so a reader can see the
agents kept to local tools. The prompts, the transcripts, the streams and
the flow's findings files stay on the host: they carry the run token and
the agents' own words (DESIGN.md, the record).

    python3 flowbench/bundle.py --logs LOGS --tag TAG --out results/TAG
"""

import argparse
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flowbench import record

# The keys anywhere in a record that hold an agent's own words: the
# result text of every agent and the merger's notes in the script arm.
AGENT_TEXT_KEYS = ("result_text", "notes")
SCORING_PATH_KEYS = ("command", "instance_log", "report")
# A host path anywhere in a string, replaced by a placeholder so a list
# keeps its length and a reader sees that something was there.
HOST_PATH = re.compile(r"(?<![\w.-])(?:/home|/tmp|/root|/mnt|/Users|/var|/opt|/private|/sessions)/[^\s\"']*")
PATH_PLACEHOLDER = "<path>"


def scrub_result(result):
    """result.json less the agents' text and the scorer's paths, with any
    other host path replaced, since a bundle carries counts, seconds,
    tokens, verdicts and the patch."""
    result = json.loads(json.dumps(result))
    scoring = result.get("scoring") or {}
    for key in SCORING_PATH_KEYS:
        scoring.pop(key, None)
    return scrub(result)


def scrub(value):
    """Any record less the agents' words, its host paths replaced."""
    if isinstance(value, dict):
        return {key: scrub(item) for key, item in value.items() if key not in AGENT_TEXT_KEYS}
    if isinstance(value, list):
        return [scrub(item) for item in value]
    if isinstance(value, str):
        return HOST_PATH.sub(PATH_PLACEHOLDER, value)
    return value


def scrub_lines(text):
    lines = []
    for line in text.splitlines():
        try:
            lines.append(json.dumps(scrub(json.loads(line)), sort_keys=True))
        except json.JSONDecodeError:
            continue
    return "".join(line + "\n" for line in lines)


def tools_called(agents_dir):
    """Each agent's tool calls by name, from its stream-json output."""
    counts = {}
    for stream in sorted(Path(agents_dir).glob("*.stream.jsonl")):
        tally = Counter()
        for line in stream.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") != "assistant":
                continue
            for block in (event.get("message") or {}).get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tally[str(block.get("name"))] += 1
        counts[stream.name[: -len(".stream.jsonl")]] = dict(sorted(tally.items()))
    return counts


def harness_report(run_dir, result):
    """The harness's report.json for the run's own run id and instance,
    so a run scored twice bundles the verdict its result.json carries."""
    scoring = result.get("scoring") or {}
    run_id, instance = scoring.get("run_id"), result.get("instance")
    if not run_id or not instance:
        return None
    reports = sorted((Path(run_dir) / "score" / "logs" / "run_evaluation" / run_id).glob(f"*/{instance}/report.json"))
    return reports[0] if len(reports) == 1 else None


def bundle_run(run_dir, out_dir):
    run_dir, out_dir = Path(run_dir), Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    result = record.read_json(run_dir / "result.json")
    record.write_json(out_dir / "result.json", scrub_result(result))
    if (run_dir / "prediction.jsonl").is_file():
        shutil.copyfile(run_dir / "prediction.jsonl", out_dir / "prediction.jsonl")
    if (run_dir / "events.jsonl").is_file():
        (out_dir / "events.jsonl").write_text(scrub_lines((run_dir / "events.jsonl").read_text(encoding="utf-8")),
                                              encoding="utf-8")
    if (run_dir / "audit.json").is_file():
        record.write_json(out_dir / "audit.json", scrub(record.read_json(run_dir / "audit.json")))
    report = harness_report(run_dir, result)
    if report:
        shutil.copyfile(report, out_dir / "report.json")
    record.write_json(out_dir / "tools.json", tools_called(run_dir / "agents"))


def attempt_number(run_dir):
    return int(run_dir.name.split("-", 1)[1]) if run_dir.name.split("-", 1)[1].isdigit() else 0


def run_directories(logs, tag):
    found = [path.parent for path in (Path(logs) / tag).glob("*/*/attempt-*/result.json")]
    return sorted(found, key=lambda run_dir: (str(run_dir.parent), attempt_number(run_dir)))


def bundle(logs, tag, out):
    done = []
    for run_dir in run_directories(logs, tag):
        relative = run_dir.relative_to(Path(logs) / tag)
        bundle_run(run_dir, Path(out) / relative)
        done.append(str(relative))
    return done


def main(argv=None):
    parser = argparse.ArgumentParser(description="Bundle a tag's runs for committing.")
    parser.add_argument("--logs", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    for line in bundle(args.logs, args.tag, args.out):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
