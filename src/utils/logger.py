"""Configuração de logging simples para uso acadêmico."""

import logging
from pathlib import Path


def setup_logger(log_dir: str = "results") -> logging.Logger:
    """Cria logger com saída em arquivo e console."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("tcc_ga")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(Path(log_dir) / "execution.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
