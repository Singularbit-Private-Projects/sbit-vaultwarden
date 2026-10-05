# vaultwarden_backup/staging.py

from pathlib import Path
import subprocess
import shutil

from .models import CommandError


class StagingArea:

    def __init__(self, config, backup_id):
        self.config = config
        self.path = (
            config.staging_directory /
            f"vaultwarden-{backup_id}"
        )

    def create(self):
        self.path.mkdir(
            parents=True,
            exist_ok=False,
        )

    def assemble(self, database_backup: Path) -> Path:
        self.create()

        command = [
            str(self.config.tar_binary),
            "-C", str(self.config.data_directory),
            "--exclude=tmp",
            "--exclude=db.sqlite3",
            "--exclude=db.sqlite3-wal",
            "--exclude=db.sqlite3-shm",
            "--exclude=db_*.sqlite3",
            "-cf", "-",
            ".",
        ]

        extract = [
            str(self.config.tar_binary),
            "-C", str(self.path),
            "-xf", "-",
        ]

        try:
            producer = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
            )

            consumer = subprocess.Popen(
                extract,
                stdin=producer.stdout,
            )

            producer.stdout.close()

            if consumer.wait() != 0 or producer.wait() != 0:
                raise CommandError("Failed to construct staging area")

            shutil.copy2(
                database_backup,
                self.path / "db.sqlite3",
            )

            return self.path

        except Exception:
            self.cleanup()
            raise

    def cleanup(self):
        shutil.rmtree(self.path, ignore_errors=True)
