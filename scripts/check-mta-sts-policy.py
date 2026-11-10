#!/usr/bin/env python3
"""Validate an MTA-STS policy file against the grammar of RFC 8461, section 3.2.

Usage: check-mta-sts-policy.py <policy-file>
Exit code 1 and one line per problem when the policy is invalid.
"""
import re
import sys

MAX_AGE_LIMIT = 31557600
FIELD = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]{0,31}):[ \t]*(.*?)[ \t]*$")
LABEL = r"(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
# RFC 8461: an mx value is a domain, optionally prefixed by "*." (wildcard of the left-most label only).
MX_PATTERN = re.compile(rf"^(\*\.)?{LABEL}(\.{LABEL})+$")
REQUIRED_ONCE = ("version", "mode", "max_age")


def check(text):
    errors = []
    lines = re.split(r"\r?\n", text)
    if lines and lines[-1] == "":
        lines.pop()
    fields = {}
    for number, line in enumerate(lines, 1):
        match = FIELD.match(line)
        if not match:
            errors.append(f"line {number}: not a 'key: value' field: {line!r}")
            continue
        fields.setdefault(match.group(1), []).append(match.group(2))

    for key in REQUIRED_ONCE:
        count = len(fields.get(key, []))
        if count != 1:
            errors.append(f"'{key}' must appear exactly once, found {count}")
    # Keys are case-sensitive; a Title Case key is an unknown extension and the real field is missing.
    for key in fields:
        if key.lower() in (*REQUIRED_ONCE, "mx") and key != key.lower():
            errors.append(f"key '{key}' must be lowercase")

    if fields.get("version", [None])[0] not in (None, "STSv1"):
        errors.append(f"version must be 'STSv1', found {fields['version'][0]!r}")
    mode = fields.get("mode", [None])[0]
    if mode not in (None, "testing", "enforce", "none"):
        errors.append(f"mode must be testing, enforce or none, found {mode!r}")
    max_age = fields.get("max_age", [None])[0]
    if max_age is not None and not (re.fullmatch(r"\d{1,10}", max_age) and int(max_age) <= MAX_AGE_LIMIT):
        errors.append(f"max_age must be an integer from 0 to {MAX_AGE_LIMIT}, found {max_age!r}")

    mx = fields.get("mx", [])
    if not mx and mode != "none":
        errors.append("at least one 'mx' is required unless mode is none")
    for value in mx:
        if not MX_PATTERN.match(value):
            errors.append(f"mx {value!r} is not a domain or a '*.' wildcard domain")
    return errors


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    with open(argv[1], encoding="utf-8") as policy:
        errors = check(policy.read())
    for error in errors:
        print(f"{argv[1]}: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
