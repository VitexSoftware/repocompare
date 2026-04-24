"""Compare two package->version mappings."""
from typing import Dict, Any


def compare_packages(a: Dict[str, str], b: Dict[str, str]) -> Dict[str, Any]:
    """Compare two dicts mapping package->version.

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
        if va == vb:
            same_versions.append({'package': name, 'version': va})
        else:
            different_versions.append({'package': name, 'a_version': va, 'b_version': vb})

    return {
        'missing_in_a': missing_in_a,
        'missing_in_b': missing_in_b,
        'same_versions': same_versions,
        'different_versions': different_versions,
    }
