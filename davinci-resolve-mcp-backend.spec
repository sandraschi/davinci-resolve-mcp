import sys, os
site_pkgs = os.path.abspath('.venv/Lib/site-packages')
if site_pkgs not in sys.path:
    sys.path.insert(0, site_pkgs)
# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for davinci-resolve-mcp backend sidecar."""

from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

pkg_name = "davinci_resolve_mcp"

datas = [(f"src/davinci_resolve_mcp", "davinci_resolve_mcp")]
for pkg in (
    "fastmcp",
    "fastapi",
    "uvicorn",
    "pydantic",
    "starlette",
    "httpx",
    "mcp",
    "opentelemetry-api",
):
    datas += copy_metadata(pkg)

hiddenimports = [
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    # Stdlib C extensions (eager import in run_server.py is not enough alone)
    "_strptime",
    "_datetime",
    # FastMCP 3.4+ JWT (authlib -> joserfc migration)
    "joserfc",
    "joserfc.jwk",
    "joserfc.jwt",
    # Common extras (calibre parity)
    "fastmcp",
    "h11",
    "beartype",
    "websockets",
    "sqlite3",
    "jwt",
    "pytz",
    "jsonschema",
    "davinci_resolve_mcp.server",
    "davinci_resolve_mcp.api",
    "davinci_resolve_mcp.api.routes",
    "davinci_resolve_mcp.main",
    "davinci_resolve_mcp.tools",
    "davinci_resolve_mcp.prompts",
]
hiddenimports += collect_submodules("davinci_resolve_mcp")
hiddenimports += collect_submodules("cachetools")
hiddenimports += collect_submodules("key_value")
for _pkg in ("cachetools", "beartype", "pytz", "jsonschema"):
    _datas, _binaries, _hidden = collect_all(_pkg)
    datas += _datas
    hiddenimports += _hidden

a = Analysis(
    ["run_server.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "pandas", "scipy", "torch", "tensorflow"],
    noarchive=True,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="davinci-resolve-mcp-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
