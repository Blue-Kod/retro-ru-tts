from setuptools import setup, Extension
import os
import sys
import glob

source_dir = os.path.join("src", "_ru_tts")

c_sources = glob.glob(os.path.join(source_dir, "*.c"))
c_sources = [s for s in c_sources if os.path.basename(s) not in ("ru_tts.c", "pyrutts.c")]

setup(
    ext_modules=[
        Extension(
            "_ru_tts_native",
            sources=c_sources + [os.path.join(source_dir, "pyrutts.c")],
            include_dirs=[source_dir],
            libraries=["m"] if sys.platform != "win32" else [],
        )
    ],
)
