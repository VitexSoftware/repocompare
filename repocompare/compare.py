"""Compare two package->version mappings."""
import re
from typing import Dict, Any, Optional

# MultiFlexi packages use a `<major>.<minor>.<patch>.<build>[~suite...]`
# scheme, e.g. `2.12.0.152~trixie`. The build number (4th component)
# increments on every CI run and must be ignored when deciding whether two
# repos ship the same release.
_BUILD_NUMBER_RE = re.compile(r'^(\d+\.\d+\.\d+)\.(\d+)(.*)$')


def normalize_version(version: Optional[str]) -> Optional[str]:
    """Strip the trailing CI build-number component from a version string.

    Versions that don't match the `major.minor.patch.build[~suite]` pattern
    are returned unchanged.
    """
    if not version:
        return version
    match = _BUILD_NUMBER_RE.match(version)
    if not match:
        return version
    base, _build, suffix = match.groups()
    return base + suffix


def compare_packages(a: Dict[str, str], b: Dict[str, str]) -> Dict[str, Any]:
    """Compare two dicts mapping package->version.

    Versions are compared ignoring the CI build-number component (see
    `normalize_version`), so e.g. `0.1.0.87~trixie` and `0.1.0.22~trixie`
    are treated as the same release.

    Returns a dict with keys: missing_in_a, missing_in_b, same_versions, different_versions
    """
    names_a = set(a.keys())
    names_b = set(b.keys())

    missing_in_a = sorted(list(names_b - names_a))
    missing_in_b = sorted(list(names_a - names_b))

    same_versions = []
    different_versions = []

    for name in sorted(names_a & names_b):
        va = a.get(name)
        vb = b.get(name)
        if normalize_version(va) == normalize_version(vb):
            same_versions.append({'package': name, 'version': va})
        else:
            different_versions.append({'package': name, 'a_version': va, 'b_version': vb})

    return {
        'missing_in_a': missing_in_a,
        'missing_in_b': missing_in_b,
        'same_versions': same_versions,
        'different_versions': different_versions,
    }
