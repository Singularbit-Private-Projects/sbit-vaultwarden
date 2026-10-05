# vaultwarden_backup/job.py

from datetime import datetime, timezone

from .models import BackupResult
from .vaultwarden import VaultwardenBackup
from .staging import StagingArea
from .validation import PayloadValidator
from .archive import ArchiveBuilder, ArchiveValidator


class BackupJob:

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

        self.vaultwarden = VaultwardenBackup(config)
        self.validator = PayloadValidator(config)
        self.archive_builder = ArchiveBuilder(config)
        self.archive_validator = ArchiveValidator(config)

    def run(self) -> BackupResult:
        backup_id = datetime.now(
            timezone.utc
        ).strftime("%Y%m%dT%H%M%SZ")

        staging = StagingArea(
            self.config,
            backup_id,
        )

        try:
            self.logger.info(
                "backup_started",
                extra={"backup_id": backup_id},
            )

            database = (
                self.vaultwarden
                .create_database_backup()
            )

            self.logger.info("database_backup_created")

            self.validator.validate_sqlite(database)

            payload = staging.assemble(database)

            self.validator.validate_payload(payload)

            archive = self.archive_builder.create(
                payload,
                backup_id,
            )

            self.archive_validator.validate(archive)

            checksum = self.archive_validator.sha256(
                archive
            )

            self.logger.info(
                "backup_completed",
                extra={
                    "backup_id": backup_id,
                    "archive": str(archive),
                    "sha256": checksum,
                },
            )

            return BackupResult(
                backup_id=backup_id,
                archive=archive,
                manifest=None,
            )

        finally:
            staging.cleanup()
