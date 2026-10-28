import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_database_url_from_environment():
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite:///custom_test.db"

    code = (
        "from app.core.config import DATABASE_URL; "
        "print(DATABASE_URL.get_backend_name()); "
        "print(DATABASE_URL.database)"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    output = result.stdout.strip().splitlines()

    assert output[-2] == "sqlite"
    assert Path(output[-1]).name == "custom_test.db"
    assert Path(output[-1]).is_absolute()
