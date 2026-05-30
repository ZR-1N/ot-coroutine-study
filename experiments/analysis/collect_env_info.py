import json
import platform
import sys
from pathlib import Path

import psutil
import pandas
import matplotlib
import requests
import aiohttp


ROOT = Path(__file__).resolve().parents[2]
SUMMARY_DIR = ROOT / "results" / "summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)


def get_env_info() -> dict:
    info = {
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version.replace("\n", " "),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "total_memory_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "aiohttp_version": aiohttp.__version__,
        "requests_version": requests.__version__,
        "psutil_version": psutil.__version__,
        "pandas_version": pandas.__version__,
        "matplotlib_version": matplotlib.__version__,
    }
    return info


def main():
    info = get_env_info()

    json_path = SUMMARY_DIR / "environment_info.json"
    txt_path = SUMMARY_DIR / "environment_info.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        for k, v in info.items():
            f.write(f"{k}: {v}\n")

    print("environment info saved to results/summary/")


if __name__ == "__main__":
    main()