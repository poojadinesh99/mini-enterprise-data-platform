"""Minimal validation helpers for ingestion examples."""
import re


def is_valid_email(email: str) -> bool:
	if not email:
		return False
	return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))
