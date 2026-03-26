import re
import sqlite3
import logging

from backend.config import settings

logger = logging.getLogger(__name__)

# Patterns that indicate write operations
WRITE_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|TRUNCATE|ATTACH|DETACH|PRAGMA\s+\w+\s*=)\b",
    re.IGNORECASE,
)


def validate_sql(sql: str) -> tuple[bool, str]:
    """Validate that SQL is read-only. Returns (is_valid, error_message)."""
    stripped = sql.strip().rstrip(";").strip()

    if not stripped.upper().startswith("SELECT"):
        return False, "Only SELECT queries are allowed"

    if WRITE_PATTERNS.search(stripped):
        return False, "Write operations are not allowed"

    # Check for multiple statements
    # Simple check: split on semicolons outside of quotes
    # More robust: just try to run it in a read-only connection
    if ";" in stripped:
        return False, "Multiple statements are not allowed"

    return True, ""


def execute_query(sql: str, max_rows: int = 100) -> dict:
    """Execute a read-only SQL query and return results."""
    is_valid, error = validate_sql(sql)
    if not is_valid:
        return {"error": error, "rows": [], "columns": []}

    db_path = settings.database_url.replace("sqlite:///", "")

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchmany(max_rows)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        result_rows = [dict(row) for row in rows]
        total = len(result_rows)
        conn.close()

        return {
            "columns": columns,
            "rows": result_rows,
            "row_count": total,
            "truncated": total >= max_rows,
        }
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        return {"error": str(e), "rows": [], "columns": []}


def get_schema_info(table_name: str | None = None) -> dict:
    """Get database schema information."""
    db_path = settings.database_url.replace("sqlite:///", "")

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        if table_name:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            conn.close()
            return {
                "table": table_name,
                "columns": [
                    {"name": c[1], "type": c[2], "nullable": not c[3], "primary_key": bool(c[5])}
                    for c in columns
                ],
            }
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'alembic%' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return {"tables": tables}
    except Exception as e:
        return {"error": str(e)}
