""" Unit tests for lib.py
"""
import json

import pandas as pd

from app import lib


def test_extract_relative_path():
    test_root_path = "/tmp/a"
    test_path = "/tmp/a/b"
    assert "a/b" == lib.extract_relative_path(test_root_path, test_path)


def test_create_content_df():
    test_data = pd.DataFrame(
        {
            "title": ["one", "two", "three"],
            "level": ["beg", "beg", "adv"],
            "url": ["url1", "url2", "url3"],
        }
    )
    content_column = ["title", "level"]
    content_df = lib.create_content_df(
        test_data, content_columns=content_column, metadata_columns="url"
    )
    a_content = content_df.content[0]
    content_dict = json.loads(a_content)
    assert "title" in list(content_dict.keys())
    assert "level" in list(content_dict.keys())
    assert len(content_dict.keys()) == len(content_column)
    assert "url" in content_df.columns
