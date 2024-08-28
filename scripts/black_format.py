import subprocess
import sys


def main() -> None:
    """Run Black formatter on the project files."""
    print("Running Black formatter...")
    try:
        # Run Black in check mode first
        result = subprocess.run(
            ["black", "--check", "."],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("All files are already formatted correctly!")
        else:
            print("Some files need formatting. Applying changes...")
            # Actually run Black to make changes
            subprocess.run(["black", "."], check=True)
            print("Formatting complete!")
    except subprocess.CalledProcessError as e:
        print("An error occurred while running Black:")
        print(e.output)
        sys.exit(1)


if __name__ == "__main__":
    main()
