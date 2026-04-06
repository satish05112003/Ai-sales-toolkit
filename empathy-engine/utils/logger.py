"""
utils/logger.py — Centralised logging setup for Empathy Engine

Creates two handlers:
  1. Console (INFO level)
  2. File: logs/emotion.log (DEBUG level, structured format)
"""

import logging
import sys
from pathlib import Path


def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """
    Configure root logger with console + file handlers.

    Args:
        log_dir: Directory where emotion.log will be written.

    Returns:
        Configured root logger.
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    log_file = log_path / "emotion.log"

    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Avoid duplicate handlers if called multiple times
    if root.handlers:
        return root

    # ── Console handler (INFO) ──────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    ))

    # ── File handler (DEBUG) ────────────────────────────────────────────
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    root.addHandler(console_handler)
    root.addHandler(file_handler)

    return root


def log_generation_event(
    logger:     logging.Logger,
    text:       str,
    emotion:    str,
    intensity:  str,
    output_file: str,
) -> None:
    """
    Log a voice generation event in a structured format.

    Args:
        logger:      Logger instance to write to.
        text:        Input text (truncated to 100 chars for log).
        emotion:     Detected emotion label.
        intensity:   Detected intensity level.
        output_file: Filename of the generated audio.
    """
    preview = text[:100].replace("\n", " ") + ("..." if len(text) > 100 else "")
    logger.info(
        f"GENERATION | emotion={emotion} | intensity={intensity} | "
        f"file={output_file} | text_preview=\"{preview}\""
    )
