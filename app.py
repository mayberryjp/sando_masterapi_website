from flask import Flask, jsonify, render_template
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", r"/database/errors.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summary")
def summary():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM error_reports")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM error_reports WHERE timestamp >= strftime('%Y%m%d000000', 'now')")
    today = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM error_reports WHERE timestamp >= strftime('%Y%m%d000000', 'now', '-7 days')")
    week = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM error_reports WHERE timestamp >= strftime('%Y%m%d000000', 'now', '-30 days')")
    month = c.fetchone()[0]
    conn.close()
    return jsonify({"total": total, "today": today, "week": week, "month": month})


@app.route("/api/errors-over-time")
def errors_over_time():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT substr(timestamp, 1, 8) as day, COUNT(*) as count
        FROM error_reports
        GROUP BY day
        ORDER BY day
    """)
    rows = c.fetchall()
    conn.close()
    data = [{"date": f"{r['day'][:4]}-{r['day'][4:6]}-{r['day'][6:8]}", "count": r["count"]} for r in rows]
    return jsonify(data)


@app.route("/api/errors-by-script-over-time")
def errors_by_script_over_time():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT substr(timestamp, 1, 8) as day, script_name, COUNT(*) as count
        FROM error_reports
        GROUP BY day, script_name
        ORDER BY day
    """)
    rows = c.fetchall()
    conn.close()

    scripts = {}
    dates = []
    for r in rows:
        date_str = f"{r['day'][:4]}-{r['day'][4:6]}-{r['day'][6:8]}"
        if date_str not in dates:
            dates.append(date_str)
        script = r["script_name"]
        if script not in scripts:
            scripts[script] = {}
        scripts[script][date_str] = r["count"]

    result = {"dates": dates, "series": {}}
    for script, counts in scripts.items():
        result["series"][script] = [counts.get(d, 0) for d in dates]

    return jsonify(result)


@app.route("/api/weekly-trend")
def weekly_trend():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT
            CAST((julianday(substr(timestamp,1,4)||'-'||substr(timestamp,5,2)||'-'||substr(timestamp,7,2))
                  - julianday('2020-01-06')) / 7 AS INTEGER) as week_num,
            MIN(substr(timestamp, 1, 8)) as week_start,
            COUNT(*) as count
        FROM error_reports
        GROUP BY week_num
        ORDER BY week_num
    """)
    rows = c.fetchall()
    conn.close()
    data = [{"week_start": f"{r['week_start'][:4]}-{r['week_start'][4:6]}-{r['week_start'][6:8]}",
             "count": r["count"]} for r in rows]
    return jsonify(data)


@app.route("/api/top-errors")
def top_errors():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT error_message, script_name, site, COUNT(*) as count,
               MAX(timestamp) as last_seen_raw
        FROM error_reports
        WHERE timestamp >= strftime('%Y%m%d%H%M%S', 'now', '-7 days')
        GROUP BY error_message, script_name, site
        ORDER BY count DESC
        LIMIT 25
    """)
    rows = c.fetchall()
    conn.close()
    now = datetime.utcnow()
    results = []
    for r in rows:
        d = dict(r)
        raw = d.pop("last_seen_raw", "")
        try:
            ts = datetime.strptime(raw, "%Y%m%d%H%M%S")
            delta = now - ts
            total_hours = int(delta.total_seconds() // 3600)
            if total_hours < 1:
                mins = int(delta.total_seconds() // 60)
                d["last_seen"] = f"{mins}m ago" if mins > 0 else "just now"
            elif total_hours < 24:
                d["last_seen"] = f"{total_hours}h ago"
            else:
                days = total_hours // 24
                d["last_seen"] = f"{days}d ago"
        except (ValueError, TypeError):
            d["last_seen"] = raw
        results.append(d)
    return jsonify(results)


@app.route("/api/recent-errors")
def recent_errors():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT error_message, script_name, file_name, site,
               COUNT(*) as count,
               MAX(timestamp) as last_seen_raw
        FROM error_reports
        WHERE timestamp >= strftime('%Y%m%d%H%M%S', 'now', '-7 days')
        GROUP BY error_message, script_name, file_name, site
        ORDER BY last_seen_raw DESC
        LIMIT 200
    """)
    rows = c.fetchall()
    conn.close()
    now = datetime.utcnow()
    results = []
    for r in rows:
        d = dict(r)
        raw = d.pop("last_seen_raw", "")
        try:
            ts = datetime.strptime(raw, "%Y%m%d%H%M%S")
            delta = now - ts
            total_hours = int(delta.total_seconds() // 3600)
            if total_hours < 1:
                mins = int(delta.total_seconds() // 60)
                d["last_seen"] = f"{mins}m ago" if mins > 0 else "just now"
            elif total_hours < 24:
                d["last_seen"] = f"{total_hours}h ago"
            else:
                days = total_hours // 24
                d["last_seen"] = f"{days}d ago"
        except (ValueError, TypeError):
            d["last_seen"] = raw
        results.append(d)
    return jsonify(results)


@app.route("/api/errors-by-script")
def errors_by_script():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT script_name, COUNT(*) as count
        FROM error_reports
        GROUP BY script_name
        ORDER BY count DESC
    """)
    rows = c.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
