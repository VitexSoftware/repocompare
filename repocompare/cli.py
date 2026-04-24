"""Command-line interface for repocompare with optional colored output via rich."""
import argparse
import json
import os
import sys

try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
except Exception:
    console = None

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    # load .env if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    repo_a_default = os.getenv('REPO_A', 'https://repo.vitexsoftware.com/')
    repo_b_default = os.getenv('REPO_B', 'https://repo.multiflexi.eu/')
    dist_default = os.getenv('DIST', 'bookworm')
    component_default = os.getenv('COMPONENT', 'main')
    arch_default = os.getenv('ARCH', 'amd64')

    p = argparse.ArgumentParser(description='Compare Debian package metadata between two APT repos')
    p.add_argument('--repo-a', default=repo_a_default, help='Base URL for repo A')
    p.add_argument('--repo-b', default=repo_b_default, help='Base URL for repo B')
    p.add_argument('--dist', default=dist_default, help='Distribution codename (e.g. bookworm)')
    p.add_argument('--component', default=component_default, help='Component (e.g. main)')
    p.add_argument('--arch', default=arch_default, help='Architecture (e.g. amd64)')
    p.add_argument('--output', choices=['text', 'json', 'both'], default='both', help='Output format')
    args = p.parse_args(argv)

    # lazy imports to keep initial import cheap
    try:
        from . import repo as repo_mod
        from . import parser as parser_mod
        from . import compare as compare_mod
    except Exception as exc:
        if console:
            console.print('Failed to import internal modules:', exc, style='bold red')
        else:
            print('Failed to import internal modules:', exc, file=sys.stderr)
        sys.exit(2)

    def load_packages(repo_url):
        try:
            found = repo_mod.fetch_first_available(repo_url, args.dist, args.component, args.arch)
        except Exception as e:
            if console:
                console.print(f'Error fetching packages from {repo_url}: {e}', style='red')
            else:
                print(f'Error fetching packages from {repo_url}: {e}', file=sys.stderr)
            return {}, None

        if not found:
            return {}, None
        text, url = found
        mapping = parser_mod.parse_packages_text(text)
        return mapping, url

    a_map, a_url = load_packages(args.repo_a)
    b_map, b_url = load_packages(args.repo_b)

    result = compare_mod.compare_packages(a_map, b_map)
    if args.output in ('text', 'both'):
        if console:
            console.print('\nComparison results:', style='bold cyan')
            console.print(f'  Repo A: {args.repo_a} (packages: {len(a_map)}) from {a_url or "(none found)"}', style='magenta')
            console.print(f'  Repo B: {args.repo_b} (packages: {len(b_map)}) from {b_url or "(none found)"}', style='magenta')
            console.print(f"  Missing in A: {len(result['missing_in_a'])}", style='red')
            console.print(f"  Missing in B: {len(result['missing_in_b'])}", style='red')
            console.print(f"  Same version: {len(result['same_versions'])}", style='green')
            console.print(f"  Different version: {len(result['different_versions'])}", style='yellow')
            if result['different_versions']:
                table = Table(title='Different versions (first 50)')
                table.add_column('Package', style='cyan', no_wrap=True)
                table.add_column('Repo A', style='green')
                table.add_column('Repo B', style='yellow')
                for diff in result['different_versions'][:50]:
                    table.add_row(diff['package'], diff.get('a_version', '-') or '-', diff.get('b_version', '-') or '-')
                console.print(table)
        else:
            print('\nComparison results:')
            print(f'  Repo A: {args.repo_a} (packages: {len(a_map)}) from {a_url or "(none found)"}')
            print(f'  Repo B: {args.repo_b} (packages: {len(b_map)}) from {b_url or "(none found)"}')
            print(f"  Missing in A: {len(result['missing_in_a'])}")
            print(f"  Missing in B: {len(result['missing_in_b'])}")
            print(f"  Same version: {len(result['same_versions'])}")
            print(f"  Different version: {len(result['different_versions'])}")

            if result['different_versions']:
                print('\nPackages with different versions (first 20):')
                for diff in result['different_versions'][:20]:
                    print(f"  {diff['package']}: A={diff['a_version']}  B={diff['b_version']}")
    if args.output in ('json', 'both'):
        if console:
            console.print('\nJSON output:', style='bold cyan')
            try:
                console.print_json(json.dumps(result))
            except Exception:
                console.print(json.dumps(result, indent=2))
        else:
            print('\nJSON output:')
            print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
"""Command-line interface for repocompare."""
import argparse
import json
import os
import sys


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    # load .env if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    repo_a_default = os.getenv('REPO_A', 'https://repo.vitexsoftware.com/')
    repo_b_default = os.getenv('REPO_B', 'https://repo.multiflexi.eu/')
    dist_default = os.getenv('DIST', 'bookworm')
    component_default = os.getenv('COMPONENT', 'main')
    arch_default = os.getenv('ARCH', 'amd64')

    p = argparse.ArgumentParser(description='Compare Debian package metadata between two APT repos')
    p.add_argument('--repo-a', default=repo_a_default, help='Base URL for repo A')
    p.add_argument('--repo-b', default=repo_b_default, help='Base URL for repo B')
    p.add_argument('--dist', default=dist_default, help='Distribution codename (e.g. bookworm)')
    p.add_argument('--component', default=component_default, help='Component (e.g. main)')
    p.add_argument('--arch', default=arch_default, help='Architecture (e.g. amd64)')
    p.add_argument('--output', choices=['text', 'json', 'both'], default='both', help='Output format')
    args = p.parse_args(argv)

    # lazy imports to keep initial import cheap
    try:
        from . import repo as repo_mod
        from . import parser as parser_mod
        from . import compare as compare_mod
    except Exception as exc:
        print('Failed to import internal modules:', exc, file=sys.stderr)
        sys.exit(2)

    def load_packages(repo_url):
        found = repo_mod.fetch_first_available(repo_url, args.dist, args.component, args.arch)
        if not found:
            return {}, None
        text, url = found
        mapping = parser_mod.parse_packages_text(text)
        return mapping, url

    a_map, a_url = load_packages(args.repo_a)
    b_map, b_url = load_packages(args.repo_b)

    result = compare_mod.compare_packages(a_map, b_map)

    if args.output in ('text', 'both'):
        print('\nComparison results:')
        print(f'  Repo A: {args.repo_a} (packages: {len(a_map)}) from {a_url or "(none found)"}')
        print(f'  Repo B: {args.repo_b} (packages: {len(b_map)}) from {b_url or "(none found)"}')
        print(f"  Missing in A: {len(result['missing_in_a'])}")
        print(f"  Missing in B: {len(result['missing_in_b'])}")
        print(f"  Same version: {len(result['same_versions'])}")
        print(f"  Different version: {len(result['different_versions'])}")

        if result['different_versions']:
            print('\nPackages with different versions (first 20):')
            for diff in result['different_versions'][:20]:
                print(f"  {diff['package']}: A={diff['a_version']}  B={diff['b_version']}")

    if args.output in ('json', 'both'):
        print('\nJSON output:')
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
