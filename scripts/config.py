# vaultwarden_backup/config.py

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class BackupConfig:
    container_name: str
    data_directory: Path
    staging_directory: Path
    output_directory: Path
    sqlite_binary: Path
    docker_binary: Path
    tar_binary: Path
    compression: str
    log_directory: Path


class ConfigLoader:
    DEFAULT_CONFIG = (
        Path(__file__).resolve().parents[1] / "config.json"
    )

    @staticmethod
    def _resolve_default_config() -> Path:
        candidate = ConfigLoader.DEFAULT_CONFIG
        if candidate.exists():
            return candidate
        return Path("/etc/vaultwarden-backup/config.json")

    def load(
        self,
        config_file: Path,
        cli_overrides: dict,
    ) -> BackupConfig:

        resolved_file = config_file or self._resolve_default_config()

        with resolved_file.open() as f:
            values = json.load(f)

        values.update({
            key: value
            for key, value in cli_overrides.items()
            if value is not None
        })

        return BackupConfig(
            container_name=values["container_name"],
            data_directory=Path(values["data_directory"]),
            staging_directory=Path(values["staging_directory"]),
            output_directory=Path(values["output_directory"]),
            sqlite_binary=Path(values["sqlite_binary"]),
            docker_binary=Path(values["docker_binary"]),
            tar_binary=Path(values["tar_binary"]),
            compression=values["compression"],
            log_directory=Path(values["log_directory"]),
        )
