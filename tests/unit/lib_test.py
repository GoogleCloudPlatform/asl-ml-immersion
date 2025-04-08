"""Unit tests for lib.py"""

from asl import lib


def test_extract_relative_path():
    test_root_path = "/tmp/a"
    test_path = "/tmp/a/b"
    assert "a/b" == lib.extract_relative_path(test_root_path, test_path)
