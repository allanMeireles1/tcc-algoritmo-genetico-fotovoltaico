"""Rotinas de exportação para JSON e CSV."""

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


def _serialize(item: Any) -> Any:
    if is_dataclass(item):
        return asdict(item)
    if isinstance(item, list):
        return [_serialize(value) for value in item]
    return item


def create_run_dir(base_dir: str = "results") -> Path:
    """Cria diretório de execução com timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(base_dir) / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def export_json(path: str | Path, data: Any) -> None:
    """Exporta qualquer estrutura serializável para JSON."""
    payload = _serialize(data)
    with Path(path).open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def export_csv(path: str | Path, rows: list[dict[str, Any]]) -> None:
    """Exporta linhas tabulares para CSV."""
    pd.DataFrame(rows).to_csv(path, index=False)
