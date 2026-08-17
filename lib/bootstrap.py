"""Bootstrap: install missing dependencies (Pillow, fonts, GIMP, engines).

    python3 run.py bootstrap          # ensure pillow + fonts, best-effort GIMP
    python3 run.py bootstrap --gimp   # also attempt a system GIMP install
    python3 run.py doctor             # probe only, no installs

Package-manager detection: pacman (Arch/Manjaro), apt-get (Debian/Ubuntu),
dnf (Fedora), zypper (openSUSE), brew (macOS). GIMP is optional — the Pillow
render path is the stable default and needs only `pillow`.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from . import ensure_dirs


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def python_bin() -> str:
    return sys.executable


def has_pillow() -> bool:
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def _install_pillow() -> bool:
    """Install Pillow, preferring uv, then pip (venv-aware)."""
    uv = shutil.which("uv")
    if uv:
        r = _run([uv, "pip", "install", "pillow", "--system"], timeout=300)
        if r.returncode == 0:
            return True
        # --system may be disallowed; fall back to a per-project venv marker
    pip = shutil.which("pip") or shutil.which("pip3")
    if pip:
        r = _run([pip, "install", "--user", "pillow"], timeout=300)
        if r.returncode == 0:
            return True
    return False


def detect_package_manager() -> str | None:
    for pm, cmd in (
        ("pacman", ["pacman", "--version"]),
        ("apt-get", ["apt-get", "--version"]),
        ("dnf", ["dnf", "--version"]),
        ("zypper", ["zypper", "--version"]),
        ("brew", ["brew", "--version"]),
    ):
        if shutil.which(cmd[0]):
            return pm
    return None


def has_gimp() -> bool:
    return bool(shutil.which("gimp") or shutil.which("gimp-console"))


def gimp_install_command(pm: str) -> list[str]:
    return {
        "pacman": ["sudo", "pacman", "-S", "--noconfirm", "gimp"],
        "apt-get": ["sudo", "apt-get", "install", "-y", "gimp"],
        "dnf": ["sudo", "dnf", "install", "-y", "gimp"],
        "zypper": ["sudo", "zypper", "--non-interactive", "install", "gimp"],
        "brew": ["brew", "install", "gimp"],
    }.get(pm, [])


def install_gimp() -> tuple[bool, str]:
    if has_gimp():
        return True, "already installed"
    pm = detect_package_manager()
    if not pm:
        return False, "no supported package manager detected"
    cmd = gimp_install_command(pm)
    if not cmd:
        return False, f"no gimp recipe for {pm}"
    r = _run(cmd, timeout=900)
    if r.returncode == 0 and has_gimp():
        return True, f"installed via {pm}"
    return False, f"install via {pm} failed (exit {r.returncode})"


def ensure_pillow() -> bool:
    if has_pillow():
        return True
    return _install_pillow()


def ensure_fonts() -> dict:
    from .fonts import ensure_fonts as ef
    return ef()


def doctor() -> dict:
    """Probe everything without installing."""
    from . import __version__
    out = {
        "program": "amtech-computer-use-graphics",
        "version": __version__,
        "python": sys.version.split()[0],
        "python_bin": python_bin(),
        "pillow": has_pillow(),
        "pillow_version": _pillow_version() if has_pillow() else None,
        "gimp": has_gimp(),
        "package_manager": detect_package_manager(),
        "cli_anything_gimp": bool(shutil.which("cli-anything-gimp")),
    }
    try:
        from .fonts import ensure_fonts as ef
        out["fonts"] = ef()
    except Exception as e:  # noqa: BLE001
        out["fonts_error"] = str(e)
    return out


def _pillow_version() -> str:
    import PIL
    return getattr(PIL, "__version__", "unknown")


def bootstrap(install_gimp: bool = False) -> dict:
    ensure_dirs()
    result: dict = {"pillow": ensure_pillow()}
    try:
        result["fonts"] = ensure_fonts()
    except Exception as e:  # noqa: BLE001
        result["fonts_error"] = str(e)
    result["gimp"] = has_gimp()
    if install_gimp and not has_gimp():
        ok, msg = globals()["install_gimp"]()
        result["gimp"] = ok
        result["gimp_install"] = msg
    elif not has_gimp():
        pm = detect_package_manager()
        result["gimp_note"] = (
            f"GIMP optional. Install with: "
            + (" ".join(gimp_install_command(pm)) if pm else "your package manager")
        )
    return result
