# VERIDEX
 
**Statistical regression testing for AI agents.**
Run each test case many times before and after a change, measure the change, measure the uncertainty, and get one of three honest answers.
 
---
 
## The problem
 
AI agents are random. The same agent, on the same test, can pass 8 times out of 10 today and 6 times out of 10 tomorrow, with nothing changed. When you edit a prompt and the pass rate drops, you cannot tell whether the drop is real or just luck.
 
VERIDEX answers with one of three verdicts:
 
| Verdict | Meaning |
|---|---|
| `REGRESSION` | It got worse than you accept, and we are confident. |
| `NO_MATERIAL_REGRESSION` | Any drop is smaller than you accept. |
| `INCONCLUSIVE` | Not enough evidence yet. It also estimates how much more data would settle it. |
 
**delta** (default `0.05`) is the biggest drop in pass rate you are willing to accept. Choose it *before* looking at results.
 
## Quickstart (no API key needed)
 
```
pip install pydantic typer jinja2 matplotlib
python examples/make_cases.py
python cli.py run examples/good_agent.py examples/cases.json --version good
python cli.py run examples/worse_agent.py examples/cases.json --version worse
python cli.py compare results/good.jsonl results/worse.jsonl
```
 
Add `--html-out report.html` to `compare` for an HTML report, or `--markdown-out comment.md` for a pull request comment. `compare` exits with code `1` on `REGRESSION` (or on `INCONCLUSIVE` with `--strict`), so CI can block a change automatically.
 
An agent is any Python function `agent(question) -> text`. A case is a question plus simple rules (`contains`, `not_contains`). Results are saved as `.jsonl`, one line per run.
 
## How it works
 
1. Every case is run N times for the old version and for the new version.
2. For each case: change = (new pass rate) - (old pass rate).
3. The cases are randomly re-picked with replacement 1,000 times (a *bootstrap*), averaging each pick. The middle 95% of those averages is the confidence range.
4. If the whole range is below `-delta`: `REGRESSION`. If the whole range is above `-delta`: `NO_MATERIAL_REGRESSION`. If it crosses `-delta`: `INCONCLUSIVE`.
The unit of resampling is the **case**, not the run, because runs of the same case are not independent evidence about the agent.
 
## Results
 
### Simulated agents (benchmark)
 
100 cases x 5 runs, 300 experiments per scenario, delta = 0.05. A "harmless" change has a true drop of 0.03 (should not be flagged). A "real" change has a true drop of 0.08 (should be flagged).
 
| Method | False alarms (harmless) | Catches (real) |
|---|---|---|
| VERIDEX, two-sided 95% range | 0.7% | 20.3% |
| VERIDEX, one-sided 95% bound | 1.7% | 32.7% |
| Naive rule, threshold 0.05 | 21.7% | 86.3% |
| Naive rule, threshold 0.07 | 5.7% | 65.0% |
| Naive rule, threshold 0.09 | 2.0% | 39.0% |
| Naive rule, threshold 0.13 | 0.0% | 3.3% |
 
*Naive rule = "flag a regression if the average pass rate dropped by more than the threshold", with no uncertainty.*
 
![false alarms vs catches](docs/benchmark_chart.png)
 
**Honest reading:** VERIDEX lands on, or slightly below, the curve of a well-tuned naive rule. It is **not** a more sensitive detector. What it adds is that it picks a safe cutoff from the data itself (the best naive threshold depends on experiment size and noise, and cannot be known in advance), it says `INCONCLUSIVE` when an experiment is too small, and it estimates how much more data is needed.
 
### A real agent
 
A LangGraph support-ticket triage agent (classify, draft a reply, quality-check loop) on a hosted LLM: `openai/gpt-oss-120b` (via Groq). 30 test tickets x 3 runs per version. Pass/fail combines label checks (category, priority), a "no `[placeholder]` in the draft" check and a step limit. Baseline pass rate: 0.856.
 
| Version | What changed | Avg. change per case | Naive rule | VERIDEX |
|---|---|---|---|---|
| v1 | nothing (identical re-run) | -0.022 | OK | INCONCLUSIVE |
| v2 | classify prompt reworded | 0.000 | OK | INCONCLUSIVE |
| v3 | placeholder bug reintroduced | -0.556 | REGRESSION | REGRESSION |
| v4 | stricter priority rule | -0.067 | REGRESSION | INCONCLUSIVE (roughly 1,500+ cases to settle) |
 
Ranges vary slightly between runs because the bootstrap is random.
 
**Honest reading:**
- No harmless change was flagged as a regression.
- The large regression (v3) is easy: every method catches it.
- On the harmless changes VERIDEX could not *confirm* "no material regression" at delta = 0.05. With 30 cases the range (about plus or minus 0.07) is wider than delta, and v1 alone, an identical agent, moved by -0.022 from run-to-run luck.
- v4 is the interesting case. The naive rule would block the change. VERIDEX says it cannot tell. The per-case report shows why: one plausible real change (a ticket labeled high priority is now rated low) mixed with drops in draft cases that v4 does not touch, which look like noise.
### In a pull request
 
VERIDEX runs on **saved** results, so CI needs no API keys and makes no model calls.
 
| Candidate | Check | Comment |
|---|---|---|
| v3 (bug back) | red X | `VERIDEX: REGRESSION` |
| v4 (strict priority) | green check | `VERIDEX: INCONCLUSIVE` |
 
![regression pull request](docs/pr_regression.png)
![inconclusive pull request](docs/pr_inconclusive.png)
 
## Other pieces in this repo
 
- `fixtures.py`: record real tool answers and replay them later, with a clear error if the agent asks for an unrecorded call. *(Library and demo only. Not wired into the CLI.)*
- `adapter.py`: runs a LangGraph graph and reports its answer, tools used and step count.
- `checks.py`: deterministic checks (right tool called, valid JSON keys, step limit, contains / not contains, expected labels).
- The runner retries on rate limits and network errors and stops loudly on a daily quota. Infrastructure errors are never counted as agent failures.
## Related work
 
Checked in October 2026 from public documentation and package pages. I did not run these tools.
 
- **agentrial** describes itself as a statistical evaluation framework for agents. Its page lists N trials per test, Wilson confidence intervals, a baseline comparison command, a LangGraph adapter and a GitHub Action.
- **Promptfoo** documents a `repeat` option that runs each test case several times.
- **Axiom** documents `trials` for running each case several times.
- Not checked yet: LangSmith, Braintrust.
What I did **not find** in those pages: a delta-based three-way verdict, resampling over cases, and CI that compares saved result files. Not finding something in a README is not proof it is absent, so treat this as a starting point, not a claim of novelty.
 
## Limitations
 
- The benchmark uses **simulated agents** with independent runs and fixed pass chances. Real agents may behave differently.
- Only **one real agent** and 30 cases were tested. The triage agent is mostly steady: about 10% of cases showed real flakiness.
- With few cases the answer is often `INCONCLUSIVE`. Cases matter more than runs, because the cases are what gets resampled.
- The "cases needed" estimate is rough, and it can swing widely for the same data.
- **delta must be chosen before looking at results.** A different delta can flip a verdict.
- Re-checking the same experiment repeatedly until it looks good raises false alarms. Sequential testing is not handled.
- CI trusts that the committed result file came from the code in the pull request.
- Expected labels in test cases are human judgment and can be wrong. Failure reasons are symptoms: one wrong priority can also cause a later draft failure.
- Cases that fail in both versions carry no information about regressions.
## Layout
 
```
folder/
  cli.py            run / compare / report / inspect
  analysis.py       comparison logic and result model
  compare.py        bootstrap range and verdict
  runner.py         runs agents, retries infrastructure errors
  checks.py         deterministic checks
  fixtures.py       tool record and replay
  adapter.py        LangGraph adapter
  report.py         HTML and markdown output
  examples/         example agents and cases
  baselines/        saved baseline results used by CI
  results/          saved runs
.github/workflows/veridex.yml
```