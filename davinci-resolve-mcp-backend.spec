# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import copy_metadata
a = Analysis(
    ['run_server.py'],
    pathex=['src'],
    datas=[('src/davinci_resolve_mcp', 'davinci_resolve_mcp')],
    hiddenimports=['uvicorn.logging','uvicorn.loops','uvicorn.loops.asyncio','uvicorn.protocols','uvicorn.protocols.http','uvicorn.protocols.http.httptools_impl','uvicorn.protocols.http.h11_impl','uvicorn.lifespan','uvicorn.lifespan.on',
    "_strptime",
],
excludes=['tkinter','setuptools','pip','wheel','test','tests','unittest','_distutils_hack','torch','torchvision','bitsandbytes','playwright','llvmlite','numba','Cython','pyarrow','pymupdf','grpc','google','azure','boto3','botocore','matplotlib','seaborn','plotly','dash','pandas','scipy','sklearn','PIL','Pillow','cv2','opencv','onnxruntime','pygame','scikit'],
    noarchive=True,
)
for pkg in ['fastapi','uvicorn','pydantic','starlette','httpx','fastmcp']:
    try: datas += copy_metadata(pkg)
    except: pass
a.datas += datas
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, name='davinci-resolve-mcp-backend', debug=False, strip=False, upx=False, upx_exclude=[],
     runtime_tmpdir=None, console=False)










