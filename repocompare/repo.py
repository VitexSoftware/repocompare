"""Helpers for fetching APT repository Packages files.

This module lazily imports network libraries so importing the package doesn't
require third-party dependencies at import-time.
"""
from typing import List, Optional
import re
from urllib.parse import urljoin


def _normalize_base(url: str) -> str:
    if not url.endswith('/'):
        url = url + '/'
    return url


def list_distributions(repo_url: str, timeout: int = 5) -> List[str]:
    """Return a list of distribution directory names found under /dists/.

    Falls back to an empty list on network or parse errors.
    """
    try:
        import requests
    except Exception:
        return []

    try:
        base = _normalize_base(repo_url)
        r = requests.get(urljoin(base, 'dists/'), timeout=timeout)
        r.raise_for_status()
        html = r.text
        # find href values ending with '/'
        matches = re.findall(r'href=["\']([^"\']+)/["\']', html)
        # fallback: any href token
        if not matches:
            matches = re.findall(r'href=["\']([^"\']+)["\']', html)
        names = []
        for m in matches:
            if m in ('..', '.', 'Parent%20Directory'):
                continue
            # basic filter - distro names are simple
            if re.match(r'^[A-Za-z0-9._-]+$', m):
                names.append(m)
        return sorted(set(names))
    except Exception:
        return []


def candidate_package_urls(repo_url: str, dist: str, component: str, arch: str) -> List[str]:
    """Generate candidate Packages file URLs (gz, bz2, xz, uncompressed).

    The caller should try each URL until one succeeds.
    """
    base = _normalize_base(repo_url).rstrip('/')
    binary_dir = f'dists/{dist}/{component}/binary-{arch}'
    exts = ['Packages.gz', 'Packages.bz2', 'Packages.xz', 'Packages']
    return [f'{base}/{binary_dir}/{e}' for e in exts]


def fetch_and_decompress(url: str, timeout: int = 20) -> Optional[str]:
    """Fetch the URL and return decompressed text, or None on 404/absent.

    Supports gzip, bzip2, xz and plain text. Raises for other HTTP errors.
    """
    try:
        import requests
        import gzip
        import bz2
        import lzma
    except Exception:
        raise

    r = requests.get(url, stream=True, timeout=timeout)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    data = r.content
    # gzip
    if url.endswith('.gz') or (len(data) >= 2 and data[:2] == b"\x1f\x8b"):
        return gzip.decompress(data).decode('utf-8', errors='replace')
    if url.endswith('.bz2'):
        return bz2.decompress(data).decode('utf-8', errors='replace')
    if url.endswith('.xz') or (len(data) >= 6 and data[:6] == b"\xfd7zXZ\x00"):
        return lzma.decompress(data).decode('utf-8', errors='replace')
    # plain
    return data.decode('utf-8', errors='replace')


def fetch_first_available(repo_url: str, dist: str, component: str, arch: str, timeout: int = 20) -> Optional[tuple]:
    """Try candidate Packages URLs and return (text, url) for the first that exists.

    Returns None if none were available.
    """
    for url in candidate_package_urls(repo_url, dist, component, arch):
        try:
            text = fetch_and_decompress(url, timeout=timeout)
            if text:
                return text, url
        except Exception:
            # keep trying other candidates
            continue
    return None
