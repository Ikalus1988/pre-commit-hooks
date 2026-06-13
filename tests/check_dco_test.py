from __future__ import annotations

import os
import tempfile

import pytest

from pre_commit_hooks.check_dco import check_dco
from pre_commit_hooks.check_dco import main


def _write_commit_msg(content: str) -> str:
    """Write a temporary commit message file and return its path."""
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
    tmp.write(content)
    tmp.close()
    return tmp.name


# ── Success cases ──


def test_standard_signoff():
    """A standard Signed-off-by line should pass."""
    msg = _write_commit_msg(
        'feat: add new feature\n'
        '\n'
        'Signed-off-by: Alice Smith <alice@example.com>\n',
    )
    try:
        code, _ = check_dco(msg)
        assert code == 0
    finally:
        os.unlink(msg)


def test_multiple_signoffs():
    """Multiple co-author sign-offs should pass."""
    msg = _write_commit_msg(
        'fix: resolve encoding issue\n'
        '\n'
        'Co-authored-by: Bob <bob@example.com>\n'
        'Signed-off-by: Alice <alice@example.com>\n'
        'Signed-off-by: Bob <bob@example.com>\n',
    )
    try:
        code, _ = check_dco(msg)
        assert code == 0
    finally:
        os.unlink(msg)


def test_signoff_in_body_not_trailer():
    """Sign-off in the middle of the body should still pass."""
    msg = _write_commit_msg(
        'docs: update readme\n'
        '\n'
        'Signed-off-by: Charlie <charlie@example.com>\n'
        '\n'
        'More content after sign-off.\n',
    )
    try:
        code, _ = check_dco(msg)
        assert code == 0
    finally:
        os.unlink(msg)


def test_signoff_with_full_name():
    """A sign-off with full name and email should pass."""
    msg = _write_commit_msg(
        'chore: bump version\n'
        '\n'
        'Signed-off-by: John Michael Doe <john.m.doe@company.com>\n',
    )
    try:
        code, _ = check_dco(msg)
        assert code == 0
    finally:
        os.unlink(msg)


def test_signoff_with_plus_email():
    """Email with + addressing should pass."""
    msg = _write_commit_msg(
        'refactor: extract method\n'
        '\n'
        'Signed-off-by: Dev <dev+feature@example.com>\n',
    )
    try:
        code, _ = check_dco(msg)
        assert code == 0
    finally:
        os.unlink(msg)


def test_multiline_commit_with_signoff():
    """A multi-paragraph commit message with a trailing sign-off."""
    msg = _write_commit_msg(
        'feat: implement BM25 search\n'
        '\n'
        'This adds BM25 scoring to the search module for\n'
        'better relevance ranking in RAG pipelines.\n'
        '\n'
        'Includes unit tests and benchmark script.\n'
        '\n'
        'Signed-off-by: Ikalus <ikalus1988@example.com>\n',
    )
    try:
        code, _ = check_dco(msg)
        assert code == 0
    finally:
        os.unlink(msg)


# ── Failure cases ──


def test_missing_signoff():
    """A commit message without any Signed-off-by line should fail."""
    msg = _write_commit_msg('fix: resolve timeout issue\n\nJust a quick fix.\n')
    try:
        code, errors = check_dco(msg)
        assert code == 1
        assert any('missing Signed-off-by' in e for e in errors)
    finally:
        os.unlink(msg)


def test_empty_message():
    """An empty commit message should fail."""
    msg = _write_commit_msg('')
    try:
        code, errors = check_dco(msg)
        assert code == 1
        assert any('missing Signed-off-by' in e for e in errors)
    finally:
        os.unlink(msg)


def test_signoff_without_email():
    """Signed-off-by: without email should fail."""
    msg = _write_commit_msg(
        'fix: typo\n'
        '\n'
        'Signed-off-by: JustName\n',
    )
    try:
        code, errors = check_dco(msg)
        assert code == 1
        assert any('malformed' in e for e in errors)
    finally:
        os.unlink(msg)


def test_signoff_without_name():
    """Signed-off-by: <email> without name should fail."""
    msg = _write_commit_msg(
        'fix: typo\n'
        '\n'
        'Signed-off-by: <anon@example.com>\n',
    )
    try:
        code, errors = check_dco(msg)
        assert code == 1
        assert any('malformed' in e for e in errors)
    finally:
        os.unlink(msg)


def test_lowercase_signoff_only():
    """lowercase 'signed-off-by:'  without proper format should fail."""
    msg = _write_commit_msg(
        'fix: typo\n'
        '\n'
        'signed-off-by: alice <alice@example.com>\n',
    )
    try:
        code, _ = check_dco(msg)
        assert code == 1
    finally:
        os.unlink(msg)


def test_signoff_only_no_colon():
    """Signed-off-by without colon should fail."""
    msg = _write_commit_msg(
        'fix: typo\n'
        '\n'
        'Signed-off-by alice <alice@example.com>\n',
    )
    try:
        code, errors = check_dco(msg)
        assert code == 1
        assert any('malformed' in e for e in errors)
    finally:
        os.unlink(msg)


# ── main() integration ──


def test_main_passes_with_valid_signoff():
    msg = _write_commit_msg(
        'feat: add search\n'
        '\n'
        'Signed-off-by: Test <test@example.com>\n',
    )
    try:
        assert main([msg]) == 0
    finally:
        os.unlink(msg)


def test_main_fails_without_signoff():
    msg = _write_commit_msg('fix: quick patch\n')
    try:
        assert main([msg]) == 1
    finally:
        os.unlink(msg)


def test_main_help():
    with pytest.raises(SystemExit):
        main(['--help'])
