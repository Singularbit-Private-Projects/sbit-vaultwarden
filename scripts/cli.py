# vaultwarden_backup/cli.py

import argparse
from pathlib import Path

from .config import ConfigLoader


def build_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        type=Path,
        default=ConfigLoader.DEFAULT_CONFIG,
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

def main():
    parser = build_parser()
    args = parser.parse_args()

    values = vars(args)

    config_file = values.pop("config")

    config = ConfigLoader().load(
        config_file,
        values,
    )

    # construct logger/job and run
