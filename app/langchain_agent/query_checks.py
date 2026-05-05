import re
import sqlparse


USER_SCOPED_TABLES = {
    "suppliers", "products", "purchase_orders", "invoices",
    "categories", "warehouses", "inventory", "purchase_order_items",
    "invoice_items", "customers", "shipments"
}

_FORBIDDEN = {"drop", "truncate", "alter", "create", "grant", "revoke"}


def _check_forbidden(sql: str) -> None:
    """Raises PermissionError if the SQL contains a forbidden keyword."""
    try:
        parsed = sqlparse.parse(sql)

        for stmt in parsed:
            for token in stmt.flatten():
                if token.ttype in sqlparse.tokens.Keyword:

                    if token.value.lower() in _FORBIDDEN:
                        raise PermissionError(f"Operation '{token.value.upper()}' is not permitted")
    except sqlparse.exceptions.SQLParseError:
        # If parsing fails, we take a conservative approach and check the raw SQL string.
        if any(kw in sql.lower() for kw in _FORBIDDEN):
            raise PermissionError("SQL contains forbidden operations")

def _extract_main_table(sql: str) -> str | None:
    """
    Returns the primary table name referenced in the SQL statement (lower-cased).
    Handles SELECT … FROM, UPDATE, INSERT INTO, DELETE FROM.
    """
    try:
        patterns = [
            r"\bDELETE\s+FROM\s+(\w+)",   # must come before plain FROM
            r"\bINSERT\s+INTO\s+(\w+)",
            r"\bUPDATE\s+(\w+)",
            r"\bFROM\s+(\w+)",
        ]
        for pat in patterns:
            m = re.search(pat, sql, re.IGNORECASE)
            if m:
                return m.group(1).lower()
    except Exception:
        pass
    return None


def _inject_user_filter(sql: str, param_index: int) -> str:
    """
    Injects `user_id = $N AND deleted = false` into the WHERE clause of a SQL statement.
    If no WHERE exists, adds one at the right position.
    """
    # If WHERE already exists, prepend filter immediately after WHERE
    try:
        if re.search(r"\bWHERE\b", sql, re.IGNORECASE):
            return re.sub(
                r"\bWHERE\b",
                f"WHERE user_id = ${param_index} AND deleted = false AND ",
                sql,
                count=1,
                flags=re.IGNORECASE,
            )

        # No WHERE — find the earliest trailing clause and inject before it
        earliest_idx = None
        for keyword in ["ORDER BY", "GROUP BY", "HAVING", "LIMIT", "OFFSET", "RETURNING"]:
            idx = sql.upper().find(keyword)
            if idx != -1 and (earliest_idx is None or idx < earliest_idx):
                earliest_idx = idx

        if earliest_idx is not None:
            return (
                sql[:earliest_idx]
                + f"WHERE user_id = ${param_index} AND deleted = false "
                + sql[earliest_idx:]
            )

        # Plain statement with no trailing clauses
        return sql.rstrip(";").rstrip() + f" WHERE user_id = ${param_index} AND deleted = false;"
    except Exception:
        return sql

def apply_query_checks(sql: str, params: list, user: dict) -> tuple[str, list]:
    """
    Rules:
    - SUPERADMIN: unrestricted (only DDL/destructive ops are blocked).
    - SUPPLIER: for tables in USER_SCOPED_TABLES:
        * SELECT / UPDATE / DELETE → user_id filter auto-injected.
        * INSERT → SQL must already include user_id column (raises
          PermissionError if it doesn't, listing the user's own user_id).

    Returns (possibly_modified_sql, possibly_extended_params).
    Raises PermissionError for policy violations.
    """
    try:    
        _check_forbidden(sql)
        params = list(params)

        if user["role"] == "SUPERADMIN":
            return sql, params
        
        # SUPPLIER enforcement
        user_id = user.get("user_id")
        if not user_id:
            raise PermissionError(
                "Access denied: SUPPLIER token is missing user_id"
            )

        table = _extract_main_table(sql)
        if not table or table not in USER_SCOPED_TABLES:
            # Table is not user-scoped; allow as-is
            return sql, params

        stmt = sql.strip().upper()

        if stmt.startswith("SELECT") or stmt.startswith("UPDATE") or stmt.startswith("DELETE"):
            params.append(user_id)
            sql = _inject_user_filter(sql, len(params))

        elif stmt.startswith("INSERT"):
            # The AI must include user_id in the INSERT; we validate but don't rewrite.
            if "user_id" not in sql.lower():
                raise PermissionError(
                    f"INSERT into '{table}' requires user association. "
                    f"The query must include the user_id column with value '{user_id}'."
                )

        return sql, params
    except PermissionError:
        raise
    except Exception as e:
        raise PermissionError(f"Failed to apply query checks: {e}")
