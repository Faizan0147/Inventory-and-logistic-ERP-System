import re
import sqlparse
# Tables with a direct supplier_id column — data is scoped per supplier.
# Directly scoped:  suppliers, products, purchase_orders, invoices
# Transitively scoped via JOIN (inventory→products, shipments→purchase_orders, etc.)
# are NOT rewritten automatically; the AI must JOIN appropriately.
SUPPLIER_SCOPED_TABLES = {"suppliers", "products", "purchase_orders", "invoices"}

# DDL / destructive keywords that are never permitted
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


def _inject_supplier_filter(sql: str, param_index: int) -> str:
    """
    Injects `supplier_id = $N` into the WHERE clause of a SQL statement.
    If no WHERE exists, adds one at the right position.
    """
    # If WHERE already exists, prepend filter immediately after WHERE
    try:
        if re.search(r"\bWHERE\b", sql, re.IGNORECASE):
            return re.sub(
                r"\bWHERE\b",
                f"WHERE supplier_id = ${param_index} AND ",
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
                + f"WHERE supplier_id = ${param_index} "
                + sql[earliest_idx:]
            )

        # Plain statement with no trailing clauses
        return sql.rstrip(";").rstrip() + f" WHERE supplier_id = ${param_index} and deleted = false;"
    except Exception:
        return sql

def apply_query_checks(sql: str, params: list, user: dict) -> tuple[str, list]:
    """
    Rules:
    - SUPERADMIN: unrestricted (only DDL/destructive ops are blocked).
    - SUPPLIER: for tables in SUPPLIER_SCOPED_TABLES:
        * SELECT / UPDATE / DELETE → supplier_id filter auto-injected.
        * INSERT → SQL must already include supplier_id column (raises
          PermissionError if it doesn't, listing the user's own supplier_id).

    Returns (possibly_modified_sql, possibly_extended_params).
    Raises PermissionError for policy violations.
    """
    try:    
        _check_forbidden(sql)
        params = list(params)

        if user["role"] == "SUPERADMIN":
            return sql, params
        # SUPPLIER enforcement
        supplier_id = user.get("supplier_id")
        if not supplier_id:
            raise PermissionError(
                "Access denied: SUPPLIER token is missing supplier_id"
            )

        table = _extract_main_table(sql)
        if not table or table not in SUPPLIER_SCOPED_TABLES:
            # Table is not supplier-scoped; allow as-is
            return sql, params

        stmt = sql.strip().upper()

        if stmt.startswith("SELECT") or stmt.startswith("UPDATE") or stmt.startswith("DELETE"):
            params.append(supplier_id)
            sql = _inject_supplier_filter(sql, len(params))

        elif stmt.startswith("INSERT"):
            # The AI must include supplier_id in the INSERT; we validate but don't rewrite.
            if "supplier_id" not in sql.lower():
                raise PermissionError(
                    f"INSERT into '{table}' must include supplier_id. "
                    f"Your supplier_id is '{supplier_id}'."
                )

        return sql, params
    except PermissionError:
        raise
    except Exception as e:
        raise PermissionError(f"Failed to apply query checks: {e}")
