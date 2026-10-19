import os
import typer
from storage import load_records
from analysis import compare_records, explain, get_case_ids, results_by_case, find_flaky_case_ids, overall_pass_rate
from report import make_report
from loader import load_agent_function, load_cases
from models import AgentResult
from runner import run_all_graph, InfraError
from storage import save_records


app = typer.Typer(help="VERIDEX: statistical regression testing for AI agents")


def load_or_exit(file_path):
    try:
        return load_records(file_path)
    except FileNotFoundError:
        typer.echo("File not found: " + file_path)
        raise typer.Exit(code=2)


@app.command()
def compare(old_file: str, new_file: str, delta: float = 0.05):
    """Compare two result files. Exit code 1 means REGRESSION."""
    old_records = load_or_exit(old_file)
    new_records = load_or_exit(new_file)

    try:
        result = compare_records(old_records, new_records, delta=delta)
    except ValueError as problem:
        typer.echo("Cannot compare: " + str(problem))
        raise typer.Exit(code=2)

    typer.echo("Cases: " + str(result.n_cases) + " | delta: " + str(result.delta))
    typer.echo("Pass rate: " + str(round(result.old_pass_rate, 3)) + " -> "
               + str(round(result.new_pass_rate, 3)))
    typer.echo("Average change per case: " + str(round(result.observed_change, 3)))
    typer.echo("95% range: " + str(round(result.low, 3)) + " to " + str(round(result.high, 3)))
    typer.echo("")
    typer.echo("VERDICT: " + result.verdict)
    typer.echo(explain(result))
    typer.echo("")
    typer.echo("(one-sided verdict: " + result.verdict_one_sided
               + " | naive rule: " + result.naive_verdict + ")")
    if len(result.flaky_cases) > 0:
        typer.echo("Flaky cases: " + ", ".join(result.flaky_cases))


        if len(result.changed_cases) > 0:
            typer.echo("")
            typer.echo("Cases whose pass rate changed (worst first):")
            for item in result.changed_cases:
                line = "  " + item.case_id + ": " + str(item.old_rate) + " -> " + str(item.new_rate)
                if len(item.reasons) > 0:
                    line = line + "  [" + "; ".join(item.reasons) + "]"
                typer.echo(line)


    if result.verdict == "REGRESSION":
        raise typer.Exit(code=1)


@app.command()
def inspect(file: str):
    """Show a summary of one result file."""
    records = load_or_exit(file)
    case_ids = get_case_ids(records)
    all_results = results_by_case(records, case_ids)
    flaky = find_flaky_case_ids(case_ids, all_results)
    errors = 0
    for record in records:
        if record.error is not None:
            errors = errors + 1
    typer.echo("Records: " + str(len(records)) + " | cases: " + str(len(case_ids)))
    typer.echo("Pass rate: " + str(round(overall_pass_rate(all_results), 3)))
    typer.echo("Agent crashes: " + str(errors))
    typer.echo("Flaky cases (" + str(len(flaky)) + "): " + ", ".join(flaky))


@app.command()
def report(old_file: str, new_file: str, out: str = "report.html", delta: float = 0.05):
    """Write an HTML report comparing two result files."""
    old_records = load_or_exit(old_file)
    new_records = load_or_exit(new_file)
    try:
        result = compare_records(old_records, new_records, delta=delta)
    except ValueError as problem:
        typer.echo("Cannot compare: " + str(problem))
        raise typer.Exit(code=2)
    make_report(result, os.path.basename(old_file), os.path.basename(new_file), out)
    typer.echo("Report written to " + out + " (verdict: " + result.verdict + ")")

@app.command()
def run(agent_file: str, cases_file: str, version: str = "run1", runs: int = 3,
        out_dir: str = "results", function_name: str = "agent"):
    """Run an agent function on every case, several times, and save the results."""
    try:
        agent_function = load_agent_function(agent_file, function_name)
        cases = load_cases(cases_file)
    except ValueError as problem:
        typer.echo("Cannot start: " + str(problem))
        raise typer.Exit(code=2)

    def agent_call(question):
        text = agent_function(question)
        return AgentResult(output=str(text))

    typer.echo("Running " + str(len(cases)) + " cases x " + str(runs) + " runs for version '" + version + "'")
    try:
        records = run_all_graph(None, cases, version, runs, None, {}, agent_call=agent_call)
    except InfraError as problem:
        typer.echo("Stopped: " + str(problem))
        raise typer.Exit(code=2)

    os.makedirs(out_dir, exist_ok=True)
    file_path = os.path.join(out_dir, version + ".jsonl")
    save_records(records, file_path)

    passed = 0
    crashed = 0
    for record in records:
        if record.passed:
            passed = passed + 1
        if record.error is not None:
            crashed = crashed + 1
    typer.echo("Saved " + str(len(records)) + " runs to " + file_path)
    typer.echo("Pass rate: " + str(round(passed / len(records), 3)) + " | agent crashes: " + str(crashed))



if __name__ == "__main__":
    app()