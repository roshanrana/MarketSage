import json
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from marketsage_core.config import Settings
from marketsage_core.models import (
    DatasetEntry,
    DependencyStatus,
    ResearchBriefData,
    ResearchBriefRequest,
    SavedResearchRunData,
)


def database_path(settings: Settings) -> Path:
    return settings.data_dir / "marketsage.duckdb"


def _ensure_audit_table(conn) -> None:
    conn.execute(
        """
        create table if not exists audit_event (
          id uuid default uuid(),
          request_id varchar not null,
          tool_name varchar not null,
          status varchar not null,
          duration_ms double not null default 0,
          mode varchar not null default 'seeded',
          warning_count integer not null default 0,
          detail varchar,
          created_at timestamp default current_timestamp
        )
        """
    )
    existing = {
        row[1] for row in conn.execute("pragma table_info('audit_event')").fetchall()
    }
    migrations = {
        "duration_ms": "alter table audit_event add column duration_ms double default 0",
        "mode": "alter table audit_event add column mode varchar default 'seeded'",
        "warning_count": (
            "alter table audit_event add column warning_count integer default 0"
        ),
        "detail": "alter table audit_event add column detail varchar",
    }
    for column, statement in migrations.items():
        if column not in existing:
            conn.execute(statement)


def ensure_database(settings: Settings) -> DependencyStatus:
    db_path = database_path(settings)
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with duckdb.connect(str(db_path)) as conn:
            _ensure_audit_table(conn)
            conn.execute(
                """
                create table if not exists dataset_manifest (
                  dataset_id varchar not null,
                  config varchar not null,
                  split varchar not null,
                  rows_count bigint,
                  license varchar,
                  source_url varchar,
                  local_status varchar,
                  checked_at timestamp default current_timestamp
                )
                """
            )
            conn.execute(
                """
                create table if not exists research_run (
                  id varchar primary key,
                  input_json varchar not null,
                  output_json varchar not null,
                  created_at timestamp default current_timestamp
                )
                """
            )
        return DependencyStatus(
            name="duckdb",
            status="ok",
            detail=f"Database ready at {db_path}",
        )
    except Exception as exc:
        return DependencyStatus(
            name="duckdb",
            status="unavailable",
            detail=f"{type(exc).__name__}: {exc}",
        )


def write_audit_event(
    settings: Settings,
    *,
    request_id: str,
    tool_name: str,
    status: str,
    duration_ms: float,
    mode: str,
    warning_count: int,
    detail: str | None = None,
) -> None:
    ensure_database(settings)
    with duckdb.connect(str(database_path(settings))) as conn:
        _ensure_audit_table(conn)
        conn.execute(
            """
            insert into audit_event (
              request_id, tool_name, status, duration_ms, mode, warning_count, detail
            )
            values (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                request_id,
                tool_name,
                status,
                duration_ms,
                mode,
                warning_count,
                detail,
            ],
        )


def write_dataset_manifest(settings: Settings, entries: list[DatasetEntry]) -> None:
    db_path = database_path(settings)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(db_path)) as conn:
        conn.execute(
            """
            create table if not exists dataset_manifest (
              dataset_id varchar not null,
              config varchar not null,
              split varchar not null,
              rows_count bigint,
              license varchar,
              source_url varchar,
              local_status varchar,
              checked_at timestamp default current_timestamp
            )
            """
        )
        conn.execute("delete from dataset_manifest")
        conn.executemany(
            """
            insert into dataset_manifest (
              dataset_id, config, split, rows_count, license, source_url, local_status
            )
            values (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    entry.dataset_id,
                    entry.config,
                    entry.split,
                    entry.rows_count,
                    entry.license,
                    entry.source_url,
                    entry.local_status,
                )
                for entry in entries
            ],
        )


def save_research_run(
    settings: Settings,
    request: ResearchBriefRequest,
    brief: ResearchBriefData,
) -> None:
    ensure_database(settings)
    with duckdb.connect(str(database_path(settings))) as conn:
        conn.execute(
            """
            insert or replace into research_run (id, input_json, output_json)
            values (?, ?, ?)
            """,
            [
                brief.run_id,
                json.dumps(request.model_dump(mode="json"), sort_keys=True),
                brief.model_dump_json(),
            ],
        )


def get_research_run(settings: Settings, run_id: str) -> SavedResearchRunData | None:
    ensure_database(settings)
    with duckdb.connect(str(database_path(settings))) as conn:
        row = conn.execute(
            """
            select id, input_json, output_json, created_at
            from research_run
            where id = ?
            """,
            [run_id],
        ).fetchone()

    if row is None:
        return None

    created_at = row[3]
    if not isinstance(created_at, datetime):
        created_at = datetime.now(UTC)

    return SavedResearchRunData(
        run_id=row[0],
        input=json.loads(row[1]),
        output=ResearchBriefData.model_validate_json(row[2]),
        created_at=created_at,
    )
