# The pilot, 2026-10-17

Source: the thread "flowbench pilot" of the project symphony2, run on
2026-10-17 from 21:54 to 22:53 UTC on the owner's word ("can you run the
pilot?"); no Claude Doc or artifact.

PLAN.md's pilot step, exactly as pre-registered: the first 8 instances of
the order (seed 0, instances.txt) under symphony, script and solo, 24
runs, one lane, claude-sonnet-5-5 at effort medium for every agent, 45
minutes per agent and 120 per run, no turn cap, the script arm with one
builder. The route was the host route inside one cloud session of the
project: `claude -p` on that session's own subscription, with run.py's
billing variables dropped, as flowbench@a7fce3c's run.py does; Claude
Code 2.1.302, SWE-bench's harness 5.0.2, the task repository at
3d07b46.

## What came out

report.md is report.py's output, unedited. In short:

- Resolved: symphony 8/8, script 8/8, solo 7/8 (pylint-dev__pylint-7080
  unresolved). No harness error, no exclusion, no orchestration failure,
  no timeout, no turn limit, every run on its first attempt.
- Tokens per instance (mean): symphony 1.01M, script 1.34M, solo 0.21M;
  paired, symphony used 0.75 of script's tokens (bootstrap over
  repositories 0.67 to 0.82) and 4.8 times solo's.
- Wall clock per run (median): symphony 91 s, script 120 s, solo 51 s.
  The whole pilot took 59 minutes and an estimated 7.86 USD at list
  prices (Claude Code's own estimate, not a bill), far under the one to
  two five-hour windows PLAN.md guessed.
- Review: symphony's reviewers raised 9 findings and its worker changed
  the code for 7; script's raised 13, its refuters confirmed 7 and its
  fixer fixed 7.

At n = 8 no comparison of resolved can reach significance (PLAN.md, What
the sample sizes can show), and none did: symphony against script is 0
discordant instances, against solo 1 to 0 (p = 1.0). What the pilot
measures is cost and time: symphony's flow cost a quarter less than the
script's on the same instances and finished faster, and both cost about
five times one agent alone in dollars (five to six times in tokens) for
one more resolved instance out of eight.

## What to read with it

- The symphony arm ran its shape only: claim, pull request, review by
  lenses, an answer to every finding, with no required check or merge
  gate between the stages (arms/symphony/README.md, PARITY.md row 15).
- The instances are easy for this model: the gold patch of each resolves
  (survey.txt), and solo resolved 7 of 8. The step of 32 is where the
  flows can disagree.
- The agents were offered the cloud session's own tools beside Claude
  Code's built-in ones (the Workflow, Artifact, Monitor and messaging
  tools among them; each agent's list is in result.json), since a child
  `claude -p` in a cloud session inherits them. Every arm was offered the
  same list, and tools.json shows what was called: Bash, Read and Write
  only, 404 calls across the 24 runs, none of the session's tools and no
  network command (audit.json).
- The audit recorded a hidden test's name in the streams of four runs
  (django-14752 under script and symphony, pylint-7080 under script and
  symphony), which by PLAN.md excludes nothing: an agent may write a test
  of the same name, and no stream named the task repository or its
  patches. On pylint-7080 it is the arms that named the test that
  resolved; whether the agents wrote it or found the name is in the
  transcripts, which stay on the host.

## The files

Each run is `<arm>/<instance>/attempt-1/`: result.json less the agents'
text (each agent's result and the merger's notes) and with the host's
paths replaced by `<path>`, prediction.jsonl (the patch scored),
events.jsonl, audit.json, report.json (the harness's verdict per test)
and tools.json, written by flowbench/bundle.py. survey.txt is the gold
patch of each instance through the same scorer before any agent ran.
