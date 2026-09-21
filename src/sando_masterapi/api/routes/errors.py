import json
from datetime import UTC, datetime
from typing import Any

from bottle import Bottle, response

from sando_masterapi.repository.errors import (
    get_summary,
    list_errors_by_script,
    list_errors_by_script_over_time,
    list_errors_over_time,
    list_recent_errors,
    list_top_errors,
    list_weekly_trend,
)


def _json(data: Any) -> str:
    response.content_type = "application/json"
    return json.dumps(data)


def _format_day(day: str) -> str:
    return f"{day[:4]}-{day[4:6]}-{day[6:8]}"


def _relative_time(raw: str) -> str:
    try:
        ts = datetime.strptime(raw, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
    except (ValueError, TypeError):
        return raw
    delta = datetime.now(UTC) - ts
    total_hours = int(delta.total_seconds() // 3600)
    if total_hours < 1:
        mins = int(delta.total_seconds() // 60)
        return f"{mins}m ago" if mins > 0 else "just now"
    if total_hours < 24:
        return f"{total_hours}h ago"
    days = total_hours // 24
    return f"{days}d ago"


def register_error_routes(app: Bottle) -> None:
    @app.get("/api/summary")
    def summary() -> str:
        return _json(get_summary())

    @app.get("/api/errors-over-time")
    def errors_over_time() -> str:
        data = [
            {"date": _format_day(r["day"]), "count": r["count"]}
            for r in list_errors_over_time()
        ]
        return _json(data)

    @app.get("/api/errors-by-script-over-time")
    def errors_by_script_over_time() -> str:
        scripts: dict[str, dict[str, int]] = {}
        dates: list[str] = []
        for r in list_errors_by_script_over_time():
            date_str = _format_day(r["day"])
            if date_str not in dates:
                dates.append(date_str)
            script = r["script_name"]
            scripts.setdefault(script, {})[date_str] = r["count"]

        result: dict[str, Any] = {"dates": dates, "series": {}}
        for script, counts in scripts.items():
            result["series"][script] = [counts.get(d, 0) for d in dates]
        return _json(result)

    @app.get("/api/weekly-trend")
    def weekly_trend() -> str:
        data = [
            {"week_start": _format_day(r["week_start"]), "count": r["count"]}
            for r in list_weekly_trend()
        ]
        return _json(data)

    @app.get("/api/top-errors")
    def top_errors() -> str:
        results = []
        for r in list_top_errors():
            d = dict(r)
            d["last_seen"] = _relative_time(d.pop("last_seen_raw", ""))
            results.append(d)
        return _json(results)

    @app.get("/api/recent-errors")
    def recent_errors() -> str:
        results = []
        for r in list_recent_errors():
            d = dict(r)
            d["last_seen"] = _relative_time(d.pop("last_seen_raw", ""))
            results.append(d)
        return _json(results)

    @app.get("/api/errors-by-script")
    def errors_by_script() -> str:
        return _json(list_errors_by_script())
