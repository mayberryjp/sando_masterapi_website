from typing import Any

from sqlalchemy import text

from sando_masterapi.db import get_engine


def get_summary() -> dict[str, int]:
    engine = get_engine()
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM error_reports")).scalar_one()
        today = conn.execute(
            text(
                "SELECT COUNT(*) FROM error_reports "
                "WHERE timestamp >= strftime('%Y%m%d000000', 'now')"
            )
        ).scalar_one()
        week = conn.execute(
            text(
                "SELECT COUNT(*) FROM error_reports "
                "WHERE timestamp >= strftime('%Y%m%d000000', 'now', '-7 days')"
            )
        ).scalar_one()
        month = conn.execute(
            text(
                "SELECT COUNT(*) FROM error_reports "
                "WHERE timestamp >= strftime('%Y%m%d000000', 'now', '-30 days')"
            )
        ).scalar_one()
    return {"total": total, "today": today, "week": week, "month": month}


def list_errors_over_time() -> list[dict[str, Any]]:
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT substr(timestamp, 1, 8) as day, COUNT(*) as count
                FROM error_reports
                GROUP BY day
                ORDER BY day
                """
            )
        ).mappings().all()
    return [dict(r) for r in rows]


def list_errors_by_script_over_time() -> list[dict[str, Any]]:
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT substr(timestamp, 1, 8) as day, script_name, COUNT(*) as count
                FROM error_reports
                GROUP BY day, script_name
                ORDER BY day
                """
            )
        ).mappings().all()
    return [dict(r) for r in rows]


def list_weekly_trend() -> list[dict[str, Any]]:
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT
                    CAST((julianday(substr(timestamp,1,4)||'-'||substr(timestamp,5,2)||'-'||substr(timestamp,7,2))
                          - julianday('2020-01-06')) / 7 AS INTEGER) as week_num,
                    MIN(substr(timestamp, 1, 8)) as week_start,
                    COUNT(*) as count
                FROM error_reports
                GROUP BY week_num
                ORDER BY week_num
                """
            )
        ).mappings().all()
    return [dict(r) for r in rows]


def list_top_errors() -> list[dict[str, Any]]:
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT error_message, script_name, site, COUNT(*) as count,
                       MAX(timestamp) as last_seen_raw
                FROM error_reports
                WHERE timestamp >= strftime('%Y%m%d%H%M%S', 'now', '-7 days')
                GROUP BY error_message, script_name, site
                ORDER BY count DESC
                LIMIT 25
                """
            )
        ).mappings().all()
    return [dict(r) for r in rows]


def list_recent_errors() -> list[dict[str, Any]]:
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT error_message, script_name, file_name, site,
                       COUNT(*) as count,
                       MAX(timestamp) as last_seen_raw
                FROM error_reports
                WHERE timestamp >= strftime('%Y%m%d%H%M%S', 'now', '-7 days')
                GROUP BY error_message, script_name, file_name, site
                ORDER BY last_seen_raw DESC
                LIMIT 200
                """
            )
        ).mappings().all()
    return [dict(r) for r in rows]


def list_errors_by_script() -> list[dict[str, Any]]:
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT script_name, COUNT(*) as count
                FROM error_reports
                GROUP BY script_name
                ORDER BY count DESC
                """
            )
        ).mappings().all()
    return [dict(r) for r in rows]
