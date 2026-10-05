# vaultwarden_backup/cli.py

import argparse
import logging
from pathlib import Path

from .config import ConfigLoader
from .job import BackupJob


def build_parser():
    parser = argparse.ArgumentParser(
        description="Create a validated Vaultwarden backup archive.",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=ConfigLoader._resolve_default_config(),
    )

    parser.add_argument("--container-name")
    parser.add_argument("--data-directory", type=Path)
    parser.add_argument("--staging-directory", type=Path)
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--sqlite-binary", type=Path)
    parser.add_argument("--docker-binary", type=Path)
    parser.add_argument("--tar-binary", type=Path)
    parser.add_argument("--compression")
    parser.add_argument("--log-directory", type=Path)

    return parser


def configure_logger(log_directory: Path) -> logging.Logger:
    log_directory.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("vaultwarden-backup")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    file_handler = logging.FileHandler(
        log_directory / "vaultwarden-backup.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    values = vars(args)
    config_file = values.pop("config")

    config = ConfigLoader().load(
        config_file,
        values,
    )

    logger = configure_logger(config.log_directory)
    job = BackupJob(config, logger)

    try:
        result = job.run()
    except Exception:
        logger.exception("backup_failed")
        raise SystemExit(1)

    print(f"Backup created: {result.archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
