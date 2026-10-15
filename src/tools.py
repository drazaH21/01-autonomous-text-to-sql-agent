import duckdb
from decimal import Decimal
from src.database import DB_PATH

def execute_sql_safely(sql_query: str) -> dict:
    """
    Safely executes a SQL query against DuckDB.
    Catches syntax or execution errors and converts Decimal types to float for JSON safety.
    Truncates results to a max of 15 rows to preserve token limits.
    """
    cleaned_query = sql_query.strip().strip("```sql").strip("```").strip()
    if not cleaned_query.lower().startswith("select"):
        return {
            "success": False,
            "error": "Security Error: Only SELECT queries are permitted for analysis."
        }

    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        result = con.execute(cleaned_query)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        con.close()

        # Convert rows to dicts and handle Decimal serialization
        formatted_results = []
        for row in rows:
            row_dict = {}
            for k, v in zip(columns, row):
                if isinstance(v, Decimal):
                    v = float(v)
                row_dict[k] = v
            formatted_results.append(row_dict)

        # Truncate to protect token budget (max 15 rows)
        is_truncated = len(formatted_results) > 15
        if is_truncated:
            formatted_results = formatted_results[:15]

        return {
            "success": True,
            "data": formatted_results,
            "row_count": len(rows),
            "truncated": is_truncated
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
