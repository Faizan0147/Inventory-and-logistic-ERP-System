from jose import JWTError, ExpiredSignatureError
from app.utils.security import decode_access_token
from fastapi import Request
from contextvars import ContextVar, Token


_CURRENT_MCP_USER: ContextVar[dict | None] = ContextVar("current_mcp_user", default=None)


def set_mcp_user_context(user: dict) -> Token:
    """Set request-like user context for in-process MCP tool calls."""
    return _CURRENT_MCP_USER.set(user)


def reset_mcp_user_context(token: Token) -> None:
    """Reset request-like user context after in-process MCP tool calls."""
    _CURRENT_MCP_USER.reset(token)


def decode_token(token: str) -> dict:
    """
    Decodes a JWT and returns {"user_id": str, "role": str, "supplier_id": str | None}.
    Raises ValueError on expired or invalid tokens.
    """
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        role = payload.get("role")
        supplier_id = payload.get("supplier_id")

        if not user_id or not role:
            raise ValueError("Token is missing required fields (user_id / role)")

        return {"user_id": user_id, "role": role, "supplier_id": supplier_id}

    except ExpiredSignatureError:
        raise ValueError("Token has expired — please log in again")
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")


def get_user_from_request(request: Request) -> dict:
    """
    Extracts the JWT from a FastAPI Request's `access_token` cookie
    (or Authorization header) and returns the decoded user dict.
    Raises ValueError if no token is found or the token is invalid.
    """
    # 1. Try cookie first (set automatically by the browser)
    token = request.cookies.get("access_token")

    # 2. Fall back to Authorization: Bearer <token> header
    if not token:
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:]

    if not token:
        raise ValueError(
            "No access_token cookie or Authorization header found — please log in"
        )

    return decode_token(token)


def get_user_from_fastmcp_request() -> dict:
    """
    Version for FastMCP context (SSE endpoints).
    Extracts JWT from the current HTTP request context within MCP.
    """
    from fastmcp.server.dependencies import get_http_request

    try:
        request = get_http_request()
    except RuntimeError:
        # Allow MCP tool execution from regular FastAPI routes that invoke tools
        # in-process (outside FastMCP's HTTP request lifecycle).
        ctx_user = _CURRENT_MCP_USER.get()
        if ctx_user:
            return ctx_user
        raise ValueError("No active HTTP request found for MCP tool call")

    # 1. Try cookie first
    token = request.cookies.get("access_token")

    # 2. Fall back to Authorization header
    if not token:
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:]

    if not token:
        raise ValueError(
            "No access_token cookie or Authorization header found — please log in"
        )

    return decode_token(token)
