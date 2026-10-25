"""Execute notebooks in fresh Jupyter kernels and reconcile aggregate CSV outputs."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import shutil
import tempfile

import nbformat
import pandas as pd
from nbclient import NotebookClient
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "validation"
DEST.mkdir(exist_ok=True)
manifest = json.loads((ROOT / "docs/reproducibility.json").read_text())
for name, expected in manifest["inputs"].items():
    actual = hashlib.sha256((ROOT / "data" / name).read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"Input changed: {name}; review the source and baseline before updating the manifest.")

results = []
for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
    nb = nbformat.read(path, as_version=4)
    nbformat.validate(nb)
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        shutil.copytree(ROOT / "data", work / "data")
        (work / "notebooks").mkdir()
        client = NotebookClient(
            nb, timeout=180, kernel_name="python3", allow_errors=False,
            resources={"metadata": {"path": str(work / "notebooks")}},
        )
        try:
            client.execute()
        finally:
            nbformat.write(nb, DEST / path.name)
        code = [c for c in nb.cells if c.cell_type == "code" and c.source.strip()]
        if not code or any(c.execution_count is None for c in code):
            raise AssertionError("Some nonempty code cells were not executed.")
        nbformat.validate(nb)
        compared = []
        for baseline in sorted((ROOT / "outputs").glob("*.csv")):
            actual = work / "outputs" / baseline.name
            if not actual.exists():
                raise AssertionError(f"Missing regenerated output: {baseline.name}")
            pd.testing.assert_frame_equal(
                pd.read_csv(baseline), pd.read_csv(actual),
                check_dtype=False, check_exact=False, rtol=1e-9, atol=1e-10,
            )
            compared.append(baseline.name)
        if not compared:
            raise AssertionError("No aggregate CSV baselines found.")
        html, _ = HTMLExporter().from_notebook_node(nb)
        (DEST / (path.stem + ".html")).write_text(html, encoding="utf-8")
        shutil.copytree(work / "outputs", DEST / (path.stem + "_outputs"), dirs_exist_ok=True)
        results.append({"notebook": path.name, "executed_code_cells": len(code),
                        "reconciled_csvs": compared, "status": "passed"})
if not results:
    raise AssertionError("No notebooks found.")
report = {"validation": "fresh native Jupyter kernel; aggregate CSV reconciliation",
          "python": platform.python_version(),
          "packages": {p: importlib.metadata.version(p) for p in
                       ["pandas", "numpy", "matplotlib", "seaborn", "scipy",
                        "nbclient", "nbformat", "nbconvert", "ipykernel"]},
          "results": results}
(DEST / "validation-report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
