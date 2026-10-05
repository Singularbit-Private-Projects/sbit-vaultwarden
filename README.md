# Vaultwarden Backup Scripts

This repository contains the local backup portion of a larger Vaultwarden disaster-recovery workflow. The goal of this component is to create a validated archive of the Vaultwarden data directory for later retention or transfer outside this project.

This project is intentionally public-safe:
- it does not include any private hostnames, usernames, or secret paths;
- the provided `config.json` uses placeholder values only;
- real deployment values should live in a private config file outside the repository.

## Scope

This component is intentionally limited to the source-side backup process. It creates a backup archive from the Vaultwarden Docker data directory and validates the result locally.

It does not perform:
- NAS mount handling;
- remote copy logic;
- SSH/SFTP/rsync transfer logic;
- cloud or NAS-specific integration.

## Project structure

- `scripts/config.py`: configuration loading and validation.
- `scripts/vaultwarden.py`: triggers Vaultwarden database backup inside the container.
- `scripts/staging.py`: prepares a staging directory by copying non-database content and replacing the live database with the freshly created backup.
- `scripts/validation.py`: validates SQLite integrity and payload structure.
- `scripts/archive.py`: creates and validates the final `tar.zst` archive.
- `scripts/job.py`: runs the backup workflow end-to-end.
- `scripts/cli.py`: command-line entrypoint.
- `config.json`: sanitized template for local overrides.

## Public-safe configuration

The repository ships with a placeholder config instead of real server paths.

Example values are intentionally generic:

```json
{
  "container_name": "vaultwarden",
  "data_directory": "/path/to/vaultwarden/data",
  "staging_directory": "/path/to/backup/staging",
  "output_directory": "/path/to/backup/output",
  "sqlite_binary": "/usr/bin/sqlite3",
  "docker_binary": "/usr/bin/docker",
  "tar_binary": "/usr/bin/tar",
  "compression": "zstd",
  "log_directory": "/path/to/backup/logs"
}
```

For a private deployment, copy this file to a local non-public location and pass it with `--config`, or keep a separate private config outside the repository.

## Requirements

The host running the scripts must have:
- Docker installed and available on `PATH`;
- SQLite CLI at the configured binary path;
- GNU tar with zstd support;
- write access to the configured staging and output directories;
- a running Vaultwarden container named by `container_name`;
- a Vaultwarden binary inside the container that supports `/vaultwarden backup`.

## Quick start

From the repository root:

```bash
python -m scripts --help
python -m scripts --config ./config.json
```

You can also override individual values directly on the command line:

```bash
python -m scripts \
  --config ./config.json \
  --container-name vaultwarden \
  --data-directory /path/to/vaultwarden/data \
  --output-directory /path/to/backup/output
```

## What the backup does

1. Runs `docker exec <container> /vaultwarden backup`.
2. Waits for a new `db_*.sqlite3` file to appear.
3. Validates the SQLite database with `PRAGMA integrity_check`.
4. Copies the active Vaultwarden directory into a staging area while excluding transient and live database files.
5. Replaces the database with the validated backup copy.
6. Builds a `.tar.zst` archive of the prepared payload.
7. Validates that the archive contains `./db.sqlite3`.
8. Logs the result and prints the generated archive path.

## Ready to test?

This project is close to runnable, but it still depends on a valid local environment. In its current form it is ready to test in a configured host environment, not as a ready-to-run standalone system in a brand-new environment without Vaultwarden and the required binaries.

## Privacy notice

Do not commit private values such as:
- hostnames;
- local directory paths;
- usernames;
- container names tied to a specific deployment;
- SSH credentials or storage endpoint details.

Keep those in a private file outside the public repository.
