import argparse
import html
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]


def find_browser(explicit_path):
    if explicit_path:
        return Path(explicit_path)

    for name in ["chromium", "chromium-browser", "google-chrome"]:
        installed = shutil.which(name)
        if installed:
            return Path(installed)

    cached = sorted((Path.home() / ".cache/ms-playwright").glob(
        "chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell"
    ))
    if cached:
        return cached[-1]

    raise SystemExit("Supply a Chromium executable using --browser.")


def saved_table(notebook_name, needle):
    notebook = nbformat.read(ROOT / "notebooks" / notebook_name, as_version=4)

    for cell in notebook.cells:
        for output in cell.get("outputs", []):
            markup = output.get("data", {}).get("text/html", "")
            if needle in markup:
                return markup

    raise ValueError(f"Saved table not found in {notebook_name}: {needle}")


def render_table(browser, notebook_name, needle, stem, title, subtitle, caveat, labels=None):
    markup = saved_table(notebook_name, needle)

    for original, display_label in (labels or {}).items():
        markup = re.sub(
            rf">\s*{re.escape(original)}\s*</th>",
            f">{html.escape(display_label)}</th>",
            markup,
        )

    stylesheet = """
        body { margin: 38px; color: #252a30; background: white; font-family: Arial, sans-serif; }
        h1 { margin: 0 0 12px; font-size: 34px; font-weight: 700; }
        .subtitle { margin: 0 0 24px; color: #526170; font-size: 23px; }
        table { width: 100%; border-collapse: collapse; font-size: 22px; }
        th, td { padding: 16px 18px !important; border: 1px solid #ccd5df; text-align: right; }
        thead th:last-child { min-width: 120px; }
        thead th { background: #edf2f7; font-weight: 600; }
        tbody th, th:first-child, tbody td.col0 { text-align: left; }
        td { font-variant-numeric: tabular-nums; }
        .note { margin-top: 24px; font-size: 21px; line-height: 1.4; }
        .source { margin-top: 12px; color: #526170; font-size: 18px; }
    """
    script = """window.onload = () => {
        document.querySelector('#metrics').textContent = JSON.stringify({
            width: document.documentElement.scrollWidth,
            bottom: Math.ceil(document.querySelector('main').getBoundingClientRect().bottom)
        });
    };"""
    document = (
        '<!doctype html><meta charset="utf-8">'
        f"<style>{stylesheet}</style><main><h1>{html.escape(title)}</h1>"
        f'<p class="subtitle">{html.escape(subtitle)}</p>{markup}'
        f'<p class="note">{html.escape(caveat)}</p>'
        f'<p class="source">Source: saved output from {html.escape(notebook_name)}. '
        'Presentation labels and styling applied; values unchanged.</p></main>'
        f'<pre id="metrics" hidden></pre><script>{script}</script>'
    )

    output = ROOT / "outputs/screenshots" / f"{stem}.png"
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="firstbyte-table-") as temporary:
        directory = Path(temporary)
        page = directory / "table.html"
        page.write_text(document, encoding="utf-8")

        command = [
            str(browser), "--headless", "--no-sandbox", "--disable-gpu",
            "--disable-background-networking", "--disable-component-update", "--disable-sync",
            f"--user-data-dir={directory / 'browser'}", "--window-size=1600,700",
            "--force-device-scale-factor=1", "--virtual-time-budget=1500", "--timeout=10000",
            f"--screenshot={output}", "--dump-dom", page.as_uri(),
        ]
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)

    match = re.search(r'<pre id="metrics" hidden[^>]*>(.*?)</pre>', result.stdout)
    metrics = json.loads(html.unescape(match.group(1))) if match else None
    if not metrics or metrics["width"] > 1600 or metrics["bottom"] > 700:
        raise ValueError(f"Screenshot layout exceeds its viewport: {metrics}")

    print(f"{output.relative_to(ROOT)}: saved table, unchanged values, no overflow")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser")
    args = parser.parse_args()
    browser = find_browser(args.browser)

    render_table(
        browser, "01_financial_trends.ipynb", "FY2024-25 (CAD)", "01_annual_comparison",
        "Year-over-year financial comparison", "FY2024–25 versus FY2025–26 · CAD",
        "Pre-gate activity proxy: purchase-date revenue less flight-date expenses; not matched accrual profit.",
        labels={"Change (%)": "YoY (%)", "&nbsp;": "Measure"},
    )

    render_table(
        browser, "05_gate_costs.ipynb", "forecast_2026_cad", "05_forecast_scenarios",
        "Gate lease forecast scenarios", "Missing 2026–2027 lease year = calendar 2026 · CAD",
        "Unchanged gate portfolio; only one annual change observed. Scenarios are not a confidence interval or contract quotes.",
        labels={
            "scenario": "Forecast assumption", "forecast_2026_cad": "2026 estimate (CAD)",
            "change_from_2025_cad": "Change from 2025 (CAD)", "change_from_2025_pct": "Change (%)",
        },
    )


if __name__ == "__main__":
    main()
