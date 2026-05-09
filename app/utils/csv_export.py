from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any

from fastapi.responses import StreamingResponse


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def build_csv_stream_response(
    *,
    rows: list[dict[str, Any]],
    columns: list[tuple[str, str]],
    filename_prefix: str,
) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([header for header, _ in columns])
    for row in rows:
        writer.writerow([_stringify(row.get(key)) for _, key in columns])

    payload = output.getvalue()
    output.close()

    month_stamp = datetime.utcnow().strftime("%Y-%m")
    filename = f"{filename_prefix}-report-{month_stamp}.csv"
    encoded = payload.encode("utf-8")
    stream = io.BytesIO(encoded)

    return StreamingResponse(
        stream,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
