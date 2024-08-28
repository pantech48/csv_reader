import subprocess
import sys


def main() -> None:
    """Run Flake8 linter on the project files."""
    try:
        subprocess.run(["flake8", "."], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(1)


if __name__ == "__main__":
    main()
