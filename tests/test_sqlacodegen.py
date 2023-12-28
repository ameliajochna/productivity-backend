import filecmp
import subprocess


def test_db() -> None:
    tmp_models_file_path = "tests/models_gen.py"
    result = subprocess.run(
        [
            "poetry",
            "run",
            "sqlacodegen",
            "postgresql://postgres_user:postgres_password@postgres:5432/postgres_db",
            "--outfile",
            tmp_models_file_path,
        ],
        capture_output=True,
    )
    print(result.stderr)
    print(result.stdout)

    pre_commit = subprocess.run(
        ["pre-commit", "run", "--files", tmp_models_file_path],
        capture_output=True,
    )
    print(pre_commit.stderr)
    print(pre_commit.stdout)
    pre_commit = subprocess.run(
        ["pre-commit", "run", "--files", tmp_models_file_path],
        capture_output=True,
    )
    print(pre_commit.stderr)
    print(pre_commit.stdout)

    assert filecmp.cmp(tmp_models_file_path, "models.py")
