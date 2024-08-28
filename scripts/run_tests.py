import pytest
import sys


def main():
    """Run the pytest suite."""
    sys.exit(pytest.main(["-v", "-s"]))


if __name__ == "__main__":
    main()
