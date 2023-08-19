"""Utils to support Flume tests."""
import os

def load_fixture(filename):
    """Load a fixture.

    Args:
        filename: File to load fixture.

    Returns:
        File fixture contents.

    """
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path) as fptr:
        return fptr.read()