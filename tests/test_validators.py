"""Unit tests for ingestion/validators.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ingestion"))

from validators import is_valid_email  # noqa: E402


def test_valid_email():
    assert is_valid_email("alice@example.com") is True


def test_valid_email_with_subdomain():
    assert is_valid_email("bob@mail.example.com") is True


def test_invalid_email_missing_at():
    assert is_valid_email("alice.example.com") is False


def test_invalid_email_missing_domain():
    assert is_valid_email("alice@") is False


def test_empty_string_is_invalid():
    assert is_valid_email("") is False


def test_none_is_invalid():
    assert is_valid_email(None) is False
