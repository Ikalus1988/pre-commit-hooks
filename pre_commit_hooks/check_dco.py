"""check-dco: verify commit messages contain a Signed-off-by line.

This hook reads the commit message file (passed as argv[1] by pre-commit
in commit-msg stage) and checks that it contains a valid
``Signed-off-by: Name <email>`` line per the Developer Certificate of Origin.

This is a pure Python implementation with no external dependencies —
only the standard library is used (``re``, ``sys``).
"""
from __future__ import annotations

import argparse
import re
from collections.abc import Sequence
from typing import Optional

DCO_PATTERN = re.compile(
    r'^Signed-off-by:\s+'
    r'(?P<name>[^<]+)'
    r'\s+'
    r'<(?P<email>[^>]+)>'
    r'\s*$',
)

EXIT_PASS = 0
EXIT_FAIL = 1


def check_dco(commit_msg_path: str) -> tuple[int, list[str]]:
    """Check a commit message file for a valid DCO sign-off.

    Returns (exit_code, diagnostic_messages).
    """
    with open(commit_msg_path, encoding='utf-8') as f:
        lines = f.read().splitlines()

    errors: list[str] = []
    found_valid = False

    for i, line in enumerate(lines, start=1):
        # Check if any line matches the DCO pattern
        if DCO_PATTERN.match(line):
            found_valid = True
        # Detect malformed sign-off attempts
        lower = line.lower().strip()
        if lower.startswith('signed-off-by'):
            if not DCO_PATTERN.match(line):
                errors.append(
                    f'{commit_msg_path}:{i}: malformed Signed-off-by line — '
                    f'expected "Signed-off-by: Name <email>"',
                )

    if not found_valid and not errors:
        # No sign-off found at all
        errors.append(
            f'{commit_msg_path}: missing Signed-off-by line. '
            f'Add "Signed-off-by: Your Name <your@email>" to the commit message.',
        )

    for err in errors:
        print(err)

    if not found_valid:
        return EXIT_FAIL, errors

    return EXIT_PASS, []


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Check that the commit message has a DCO sign-off.',
    )
    parser.add_argument(
        'commit_msg_file',
        help='Path to the commit message file (provided by pre-commit).',
    )
    args = parser.parse_args(argv)

    exit_code, _ = check_dco(args.commit_msg_file)
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
