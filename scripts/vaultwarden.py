# vaultwarden_backup/vaultwarden.py

from pathlib import Path
import subprocess
import time

from .models import CommandError


class VaultwardenBackup:

    def __init__(self, config):
        self.config = config

    def create_database_backup(self) -> Path:
        before = set(
            self.config.data_directory.glob("db_*.sqlite3")
        )

        command = [
            str(self.config.docker_binary),
            "exec",
            self.config.container_name,
            "/vaultwarden",
            "backup",
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise CommandError(
                f"Vaultwarden backup failed: {result.stderr.strip()}"
            )

        deadline = time.monotonic() + 10

        while time.monotonic() < deadline:
            candidates = (
                set(self.config.data_directory.glob("db_*.sqlite3"))
                - before
            )

            if candidates:
                return max(
                    candidates,
                    key=lambda p: p.stat().st_mtime_ns,
                )

            time.sleep(0.1)

        raise CommandError(
            "Vaultwarden backup completed but no database backup appeared"
        )
