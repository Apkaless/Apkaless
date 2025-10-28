import ast
import os
import subprocess
import sys
from typing import Dict, Iterable, List, Set, Tuple


def _get_top_level_imports(filepath: str) -> Set[str]:
    """Parse imports using AST and return top-level module names (first segment before a dot).

    - Skips relative imports (from . import x)
    - Deduplicates results
    """
    with open(filepath, "r", encoding="utf8") as f:
        source = f.read()
    tree = ast.parse(source, filename=filepath)

    imports: Set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if not alias.name:
                    continue
                top = alias.name.split(".")[0].strip()
                if top:
                    imports.add(top)
        elif isinstance(node, ast.ImportFrom):
            # Skip relative imports like from . or from ..pkg
            if getattr(node, "level", 0):
                continue
            if node.module:
                top = node.module.split(".")[0].strip()
                if top:
                    imports.add(top)
    return imports


def _stdlib_modules() -> Set[str]:
    """Return a conservative set of standard library top-level modules to exclude.

    Note: This is a curated subset for practical filtering without external deps.
    """
    return {
        # Core/builtins/common stdlib
        "sys",
        "os",
        "re",
        "json",
        "subprocess",
        "ctypes",
        "binascii",
        "random",
        "time",
        "datetime",
        "socket",
        "threading",
        "concurrent",
        "typing",
        "dataclasses",
        "logging",
        "pathlib",
        "functools",
        "itertools",
        "collections",
        "hashlib",
        "hmac",
        "queue",
        "http",
        "urllib",
        "argparse",
        "email",
        "html",
        "math",
        "statistics",
        "traceback",
        "multiprocessing",
        "shutil",
        "tempfile",
        "gzip",
        "zipfile",
        "tarfile",
        "uuid",
        "enum",
        "inspect",
        "platform",
        "getpass",
        "secrets",
        "selectors",
        "signal",
        "sched",
        "weakref",
        "base64",
        "asyncio",
        "csv",
        "sqlite3",
        "venv",
        "distutils",
        "ensurepip",
        "importlib",
        "pkgutil",
    }


def _pypi_name_map() -> Dict[str, str]:
    """Map common import names to PyPI package names."""
    return {
        "PIL": "Pillow",
        "cv2": "opencv-python",
        "skimage": "scikit-image",
        "sklearn": "scikit-learn",
        "yaml": "PyYAML",
        "Crypto": "pycryptodome",
        "bs4": "beautifulsoup4",
        "lxml": "lxml",
        "ujson": "ujson",
        "orjson": "orjson",
        "pydantic": "pydantic",
        "requests": "requests",
        "aiohttp": "aiohttp",
        "websockets": "websockets",
        "selenium": "selenium",
        "pyautogui": "PyAutoGUI",
        "playsound": "playsound",
        "dateutil": "python-dateutil",
        "dotenv": "python-dotenv",
        "psutil": "psutil",
        "pymysql": "PyMySQL",
        "mysql": "mysqlclient",
        "pymongo": "pymongo",
        "redis": "redis",
        "colorama": "colorama",
        "rich": "rich",
        "tqdm": "tqdm",
        "beautifulsoup4": "beautifulsoup4",
        "duckduckgo_search": "duckduckgo-search",
        "discord": "discord.py",
        "pycord": "py-cord",
        "win32crypt": "pywin32"
    }


def _to_pypi_name(module_name: str) -> str:
    """Translate an import name to its expected PyPI package name if needed."""
    return _pypi_name_map().get(module_name, module_name)


def discover_third_party_packages(filepath: str) -> List[str]:
    """Return a sorted list of likely third-party package names for installation."""
    imported = _get_top_level_imports(filepath)
    stdlib = _stdlib_modules()

    third_party: Set[str] = set()
    for name in imported:
        if name in stdlib:
            continue
        # Filter obvious dunder or private
        if not name or name.startswith("_"):
            continue
        third_party.add(_to_pypi_name(name))

    return sorted(third_party)


def write_requirements(packages: Iterable[str], output_path: str = "requirements_autogen.txt") -> str:
    """Write packages to a requirements file (one per line) and return the path."""
    packages = list(dict.fromkeys(pkg.strip() for pkg in packages if pkg and pkg.strip()))
    with open(output_path, "w", encoding="utf8") as f:
        for pkg in packages:
            f.write(f"{pkg}\n")
    return output_path


def install_packages(packages: Iterable[str]) -> Tuple[List[str], List[Tuple[str, str]]]:
    """Install each package via pip. Returns (installed, failures[(pkg, error_msg)])."""
    installed: List[str] = []
    failures: List[Tuple[str, str]] = []

    for pkg in packages:
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", pkg]
        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if proc.returncode == 0:
                installed.append(pkg)
            else:
                failures.append((pkg, proc.stderr.strip() or proc.stdout.strip()))
        except Exception as exc:  # Only around external process
            failures.append((pkg, str(exc)))
    return installed, failures


def install_requirements_lib(fpath: str):
    """Discover third-party imports for a Python file, write requirements, and install them."""
    if not os.path.isfile(fpath):
        raise FileNotFoundError(f"File not found: {fpath}")

    packages = discover_third_party_packages(fpath)
    print(f"Discovered third-party packages: {packages}")

    if packages:
        req_path = write_requirements(packages)
        print(f"Wrote {len(packages)} packages to {req_path}")
        return True
        # installed, failures = install_packages(packages)
        # if installed:
        #     print(f"Installed: {installed}")
        # if failures:
        #     print("Failed installs:")
        #     for pkg, msg in failures:
        #         print(f"  - {pkg}: {msg}")
    else:
        print("No third-party packages detected.")
        return False

if __name__ == "__main__":
    # Default target file; adjust as needed
    install_requirements_lib('d_t.py')