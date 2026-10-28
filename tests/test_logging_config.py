import json
import logging

from app.core.logging_config import JsonFormatter


def test_json_formatter_outputs_valid_json():
    formatter = JsonFormatter()

    record = logging.LogRecord(
        name="app.main",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Request completed",
        args=(),
        exc_info=None,
    )

    output = formatter.format(record)
    data = json.loads(output)

    assert data["level"] == "INFO"
    assert data["logger"] == "app.main"
    assert data["message"] == "Request completed"
    assert "timestamp" in data
