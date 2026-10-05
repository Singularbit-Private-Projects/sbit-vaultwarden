# vaultwarden_backup/archive.py

from pathlib import Path
import hashlib
import subprocess

from .models import CommandError


class ArchiveBuilder:

    def __init__(self, config):
        self.config = config

    def create(self, payload: Path, backup_id: str) -> Path:
        temporary = (
            self.config.output_directory /
            f"vaultwarden-{backup_id}.tar.zst.tmp"
        )

        final = (
            self.config.output_directory /
            f"vaultwarden-{backup_id}.tar.zst"
        )

        self.config.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        command = [
            str(self.config.tar_binary),
            "--zstd",
            "-C", str(payload),
            "-cf", str(temporary),
            ".",
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            temporary.unlink(missing_ok=True)
            raise CommandError(result.stderr.strip())

        temporary.replace(final)

        return final


class ArchiveValidator:

    def __init__(self, config):
        self.config = config

    def validate(self, archive: Path):
        result = subprocess.run(
            [
                str(self.config.tar_binary),
                "--zstd",
                "-tf",
                str(archive),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise CommandError(
                f"Archive validation failed: "
                f"{result.stderr.strip()}"
            )

        if "./db.sqlite3" not in result.stdout:
            raise CommandError(
                "Archive does not contain db.sqlite3"
            )

    @staticmethod
    def sha256(path: Path) -> str:
        digest = hashlib.sha256()

        with path.open("rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(block)

        return digest.hexdigest()
