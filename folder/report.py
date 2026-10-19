import base64
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from jinja2 import Template
from analysis import explain

PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>VERIDEX report</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 760px; margin: 30px auto; padding: 0 16px; color: #222; }
  .verdict { padding: 18px; border-radius: 8px; color: white; font-size: 26px; font-weight: bold; }
  .REGRESSION { background: #c0392b; }
  .NO_MATERIAL_REGRESSION { background: #2e8b57; }
  .INCONCLUSIVE { background: #d68910; }
  table { border-collapse: collapse; width: 100%; margin: 16px 0; }
  td, th { border: 1px solid #ddd; padding: 8px; text-align: left; }
  th { background: #f3f3f3; }
  .small { color: #666; font-size: 13px; }
  img { max-width: 100%; }
</style>
</head>
<body>
<h1>VERIDEX report</h1>
<p class="small">Old: {{ old_name }} &nbsp;|&nbsp; New: {{ new_name }}</p>

<div class="verdict {{ result.verdict }}">{{ result.verdict }}</div>
<p>{{ explanation }}</p>

<img src="data:image/png;base64,{{ chart }}" alt="Range chart">

<table>
  <tr><th>Cases compared</th><td>{{ result.n_cases }}</td></tr>
  <tr><th>Delta (biggest drop you accept)</th><td>{{ result.delta }}</td></tr>
  <tr><th>Pass rate (old to new)</th><td>{{ old_rate }} to {{ new_rate }}</td></tr>
  <tr><th>Average change per case</th><td>{{ change }}</td></tr>
  <tr><th>95% range of the change</th><td>{{ low }} to {{ high }}</td></tr>
  <tr><th>One-sided verdict</th><td>{{ result.verdict_one_sided }}</td></tr>
  <tr><th>Naive rule (no uncertainty)</th><td>{{ result.naive_verdict }}</td></tr>
  <tr><th>Flaky cases</th><td>{% if result.flaky_cases %}{{ result.flaky_cases | join(", ") }}{% else %}none{% endif %}</td></tr>
</table>

{% if result.changed_cases %}
<h3>Cases whose pass rate changed (worst first)</h3>
<table>
  <tr><th>Case</th><th>Old to new</th><th>Why it failed in the new version</th></tr>
  {% for item in result.changed_cases %}
  <tr><td>{{ item.case_id }}</td><td>{{ item.old_rate }} to {{ item.new_rate }}</td><td>{{ item.reasons | join("; ") }}</td></tr>
  {% endfor %}
</table>
{% endif %}

<h3>How to read this</h3>
<p class="small">The blue bar is the 95% range of the change in pass rate, found by resampling the cases.
The red dashed line is -delta, the biggest drop you said you accept.
If the whole bar is left of the line: REGRESSION. If the whole bar is right of it: NO_MATERIAL_REGRESSION.
If the bar crosses the line: INCONCLUSIVE (not enough evidence yet).</p>

<h3>Limits</h3>
<p class="small">Delta must be chosen before looking at results. Checking the same experiment again and again until it looks good
raises the false-alarm rate. The "cases needed" estimate is rough.</p>
</body>
</html>
"""


def make_range_chart(result):
    figure, axis = plt.subplots(figsize=(7, 2.6))

    left_edge = min(result.low, -result.delta) - 0.05
    right_edge = max(result.high, 0.0) + 0.05
    axis.set_xlim(left_edge, right_edge)
    axis.set_ylim(-1, 1)

    axis.axvspan(left_edge, -result.delta, color="#f8d7da", alpha=0.7)
    axis.axvline(-result.delta, color="red", linestyle="--")
    axis.axvline(0, color="gray", linewidth=1)
    axis.plot([result.low, result.high], [0, 0], linewidth=9, color="#4a6fa5", solid_capstyle="butt")
    axis.plot([result.observed_change], [0], marker="o", markersize=11,
              markerfacecolor="white", markeredgecolor="black")
    axis.text(-result.delta, 0.55, " -delta", color="red", fontsize=9)

    axis.set_yticks([])
    axis.set_xlabel("Change in pass rate (new minus old)")
    axis.set_title("95% range of the change (dot = observed)", fontsize=10)

    buffer = io.BytesIO()
    figure.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(figure)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def make_report(result, old_name, new_name, output_path):
    page = Template(PAGE, autoescape=True)
    html = page.render(
        result=result,
        explanation=explain(result),
        chart=make_range_chart(result),
        old_name=old_name,
        new_name=new_name,
        old_rate=round(result.old_pass_rate, 3),
        new_rate=round(result.new_pass_rate, 3),
        change=round(result.observed_change, 3),
        low=round(result.low, 3),
        high=round(result.high, 3),
    )
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html)
    return output_path