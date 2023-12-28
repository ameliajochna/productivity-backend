import filecmp
import json
import subprocess

from fastapi.openapi.utils import get_openapi

from main import app


def test_openapi():
    tmp_openapi_file_path = "tests/openapi_gen.json"

    with open(tmp_openapi_file_path, "w") as f:
        json.dump(
            get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                routes=app.routes,
            ),
            f,
        )

    pre_commit = subprocess.run(
        ["pre-commit", "run", "--files", tmp_openapi_file_path], capture_output=True
    )
    print(pre_commit.stderr)
    print(pre_commit.stdout)
    pre_commit = subprocess.run(
        ["pre-commit", "run", "--files", tmp_openapi_file_path], capture_output=True
    )
    print(pre_commit.stderr)
    print(pre_commit.stdout)

    assert filecmp.cmp(tmp_openapi_file_path, "openapi.json")
