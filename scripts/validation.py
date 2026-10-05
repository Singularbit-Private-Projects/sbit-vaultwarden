# vaultwarden_backup/validation.py

import sqlite3
import subprocess

from .models import ValidationError


class PayloadValidator:

    def __init__(self, config):
        self.config = config

    def validate_sqlite(self, database):
        result = subprocess.run(
            [
                str(self.config.sqlite_binary),
                str(database),
                "PRAGMA integrity_check;",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise ValidationError(
                f"SQLite validation failed: {result.stderr.strip()}"
            )

        if result.stdout.strip() != "ok":
            raise ValidationError(
                f"SQLite integrity check returned: "
                f"{result.stdout.strip()!r}"
            )

    def validate_payload(self, payload):
        database = payload / "db.sqlite3"

        if not database.is_file():
            raise ValidationError("Payload has no db.sqlite3")

        required = [
            payload / "rsa_key.pem",
        ]

        for path in required:
            if not path.exists():
                raise ValidationError(
                    f"Required payload item missing: {path.name}"
                )
