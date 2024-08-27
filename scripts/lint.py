import subprocess
import sys


def main():
    try:
        subprocess.run(["flake8", "."], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(1)


if __name__ == "__main__":
    main()
