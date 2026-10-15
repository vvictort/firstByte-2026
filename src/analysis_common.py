import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".venv/matplotlib"))
os.environ.setdefault("IPYTHONDIR", str(ROOT / ".venv/ipython"))

import matplotlib.pyplot as plt
import pandas as pd

FY_ORDER = ["FY2024-25", "FY2025-26"]
COLORS = {"blue": "#275D86", "gold": "#C38A28", "orange": "#C76943",
          "olive": "#6E7F45", "pink": "#AE6F91", "grey": "#747B83"}
DATE_ASSUMPTION = (
    "Interpret the 7,902 originally ambiguous transaction dates as DD/MM/YYYY "
    "(day first), as requested. These retain date_status=assumed_day_first and "
    "their original date strings. Of these, 759 fall outside September 2024–August 2026; "
    "reconcile those separately when reporting fiscal-year results. "
    "Transaction timestamps measure purchase activity; cost timestamps measure flights."
)


def load_data(name):
    frame = pd.read_csv(ROOT / "data/processed" / f"{name}.csv", dtype=str, keep_default_na=False)
    money = "annual_gate_cost" if "annual_gate_cost" in frame else "amount" if "amount" in frame else None
    if money:
        frame[money + "_cents"] = pd.to_numeric(frame[money]).mul(100).round().astype("int64")
        frame[money] = frame[money + "_cents"] / 100
    if "assigned_route_count" in frame:
        frame["assigned_route_count"] = pd.to_numeric(frame["assigned_route_count"])
    date = {"transactions": "transaction_date", "costs": "cost_date"}.get(name)
    if date:
        frame[date] = pd.to_datetime(frame[date], format="%Y-%m-%d %H:%M:%S", errors="raise")
        frame["fiscal_year"] = "Outside study period"
        for label, start, end in [(FY_ORDER[0], "2024-09-01", "2025-09-01"),
                                  (FY_ORDER[1], "2025-09-01", "2026-09-01")]:
            frame.loc[frame[date].ge(start) & frame[date].lt(end), "fiscal_year"] = label
        frame["in_scope"] = frame["fiscal_year"].isin(FY_ORDER)
        frame["month"] = frame[date].dt.strftime("%Y-%m")
    return frame


def setup_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.titlesize": 15, "axes.labelsize": 11, "figure.figsize": (10.5, 5.8),
        "figure.facecolor": "white", "axes.facecolor": "white", "text.color": "#252A30",
        "axes.labelcolor": "#252A30", "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "savefig.dpi": 180,
        "axes.prop_cycle": plt.cycler(color=list(COLORS.values())),
    })


def save_figure(fig, stem):
    directory = ROOT / "outputs/figures"
    directory.mkdir(parents=True, exist_ok=True)
    paths = (directory / f"{stem}.png", directory / f"{stem}.svg")
    for path in paths:
        fig.savefig(path, bbox_inches="tight", facecolor="white")
    return paths


def save_table(frame, stem, index=False):
    directory = ROOT / "outputs/tables"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{stem}.csv"
    frame.to_csv(path, index=index)
    return path


def execute_notebook(path):
    import nbformat
    from nbclient import NotebookClient

    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".venv/matplotlib"))
    os.environ.setdefault("IPYTHONDIR", str(ROOT / ".venv/ipython"))
    os.environ["JUPYTER_PATH"] = str(ROOT / ".venv/share/jupyter")
    path = Path(path)
    notebook = nbformat.read(path, as_version=4)
    notebook.metadata.kernelspec = {"display_name": "Python (FirstByte)", "language": "python", "name": "firstbyte"}
    client = NotebookClient(notebook, timeout=600, kernel_name="firstbyte", resources={"metadata": {"path": str(ROOT)}})
    client.execute()
    nbformat.write(notebook, path)
    return notebook
