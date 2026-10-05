# vaultwarden_backup/models.py

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BackupResult:
    backup_id: str
    archive: Path
    manifest: Path

class BackupError(Exception):
    """Expected backup failure."""


class ValidationError(BackupError):
    """Backup validation failed."""


class CommandError(BackupError):
    """External command failed."""

