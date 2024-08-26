import subprocess
import sys


def main():
    try:
        subprocess.run(["flake8", "."], check=True)
        print("Linting passed successfully!")
    except subprocess.CalledProcessError as e:
        print("Linting found issues:")
        print(e.output.decode() if e.output else "No output captured")
        sys.exit(1)


if __name__ == "__main__":
    main()