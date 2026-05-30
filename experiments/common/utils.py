from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "results" / "raw"
PLOTS_DIR = ROOT / "results" / "plots"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def append_results_csv(filename: str, rows: list[dict]) -> None:
    path = RAW_DIR / filename
    df = pd.DataFrame(rows)
    if path.exists():
        old = pd.read_csv(path)
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def write_results_csv(filename: str, rows: list[dict]) -> None:
    path = RAW_DIR / filename
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False, encoding="utf-8-sig")