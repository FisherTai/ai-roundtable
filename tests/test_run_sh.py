import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import textwrap
import unittest


def write_executable(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class RunShTestCase(unittest.TestCase):
    def test_run_sh_recreates_moved_venv_with_unquoted_activate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            project_dir = tmp_path / "project"
            project_dir.mkdir()

            shutil.copy2("run.sh", project_dir / "run.sh")
            os.chmod(project_dir / "run.sh", 0o755)

            (project_dir / "app.py").write_text("print('placeholder app')\n")
            (project_dir / "requirements.txt").write_text("")

            venv_dir = project_dir / "venv"
            venv_bin_dir = venv_dir / "bin"
            venv_bin_dir.mkdir(parents=True)

            write_executable(
                venv_bin_dir / "python",
                "#!/bin/sh\nexit 0\n",
            )
            write_executable(
                venv_bin_dir / "activate",
                textwrap.dedent(
                    """
                    VIRTUAL_ENV=/tmp/stale-venv
                    export VIRTUAL_ENV
                    PATH="$VIRTUAL_ENV/bin:$PATH"
                    export PATH
                    """
                ).strip()
                + "\n",
            )

            requirements_hash = hashlib.sha256(b"").hexdigest()
            (venv_dir / ".requirements.sha256").write_text(f"{requirements_hash}\n")

            helper_dir = tmp_path / "helpers"
            helper_dir.mkdir()
            write_executable(
                helper_dir / "python3.11",
                """#!/bin/sh
if [ "$1" = "-c" ]; then
  echo "3.11"
  exit 0
fi

if [ "$1" = "-m" ] && [ "$2" = "venv" ]; then
  target="$3"
  mkdir -p "$target/bin"
  cat > "$target/bin/python" <<'EOF'
#!/bin/sh
exit 0
EOF
  cat > "$target/bin/pip" <<'EOF'
#!/bin/sh
exit 0
EOF
  cat > "$target/bin/streamlit" <<'EOF'
#!/bin/sh
echo "STREAMLIT_OK:$@"
EOF
  cat > "$target/bin/activate" <<EOF
VIRTUAL_ENV="$target"
export VIRTUAL_ENV
PATH="$target/bin:\$PATH"
export PATH
EOF
  chmod +x "$target/bin/python" "$target/bin/pip" "$target/bin/streamlit"
  exit 0
fi

echo "unexpected args: $@" >&2
exit 1
""",
            )

            env = os.environ.copy()
            env["PATH"] = f"{helper_dir}{os.pathsep}{env['PATH']}"

            result = subprocess.run(
                ["bash", "./run.sh", "--server.port", "9999"],
                cwd=project_dir,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("STREAMLIT_OK:run", result.stdout)


if __name__ == "__main__":
    unittest.main()
