repocompare
===========

Small CLI tool to compare package names and versions between two APT repositories.

Quickstart

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Edit `.env` or pass CLI flags. Example:

```bash
python -m repocompare --repo-a https://repo.vitexsoftware.com/ --repo-b https://repo.multiflexi.eu/ --dist bookworm --component main --arch amd64
```

Outputs a summary and JSON payload describing missing and differing packages.

Colored output

If `rich` is installed (it's in `requirements.txt`), the CLI will print a colored summary and a table of differing packages. If `rich` is not available the CLI falls back to plain text output.

Packaging (Debian .deb)

To build a Debian package of `repocompare` using the included `debian/` directory:

1. Install Debian build dependencies on a Debian/Ubuntu system:

```bash
sudo apt update
sudo apt install -y debhelper-compat dh-python python3-all python3-setuptools build-essential
```

2. Build the binary package from the project root:

```bash
dpkg-buildpackage -us -uc -b
```

3. The resulting `.deb` will be in the parent directory. Install with:

```bash
sudo dpkg -i ../repocompare_0.1.0-1_all.deb
```

Note: Building on non-Debian systems or in CI may require additional tooling. The package uses `dh-python` and `setuptools` to install the Python module and the `repocompare` console entry point.

