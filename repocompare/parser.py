"""Simple Debian 'Packages' control-file parser.

This is a lightweight parser that extracts `Package` and `Version` fields from a
Packages-style control file. It does not require the `debian` package and is
intended to be robust for basic metadata extraction.
"""
from typing import Dict


def parse_packages_text(text: str) -> Dict[str, str]:
    """Parse Packages file text and return mapping package -> version.

    If the same package appears multiple times, the first occurrence is kept.
    """
    packages = {}
    current = {}
    last_key = None

    for raw_line in text.splitlines():
        # preserve trailing spaces for continuation detection
        line = raw_line.rstrip('\n')
        if not line.strip():
            # end of block
            if 'Package' in current and 'Version' in current:
                name = current['Package']
                ver = current['Version']
                if name not in packages:
                    packages[name] = ver
            current = {}
            last_key = None
            continue

        # continuation lines start with space or tab
        if line.startswith(' ') or line.startswith('\t'):
            if last_key and last_key in current:
                current[last_key] = current[last_key] + '\n' + line.lstrip()
            continue

        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            current[key] = val
            last_key = key
        else:
            # malformed line - ignore
            last_key = None
            continue

    # final block
    if 'Package' in current and 'Version' in current:
        name = current['Package']
        ver = current['Version']
        if name not in packages:
            packages[name] = ver

    return packages
