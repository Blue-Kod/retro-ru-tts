from setuptools import setup, find_packages, Extension
import os
import sys
import glob

source_dir = os.path.join("src", "_ru_tts")

c_sources = glob.glob(os.path.join(source_dir, "*.c"))
c_sources = [s for s in c_sources if os.path.basename(s) not in ("ru_tts.c", "pyrutts.c")]

pyrutts = Extension(
    "_ru_tts_native",
    sources=c_sources + [os.path.join(source_dir, "pyrutts.c")],
    include_dirs=[source_dir],
    libraries=["m"] if sys.platform != "win32" else [],
)

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="retro-ru-tts",
    version="1.0.0",
    description="Retro Russian speech synthesizer (ru_tts) wrapped for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Loginov Andrey",
    url="https://github.com/Blue-Kod/retro-ru-tts",
    project_urls={
        "Source": "https://github.com/Blue-Kod/retro-ru-tts",
        "Original repository": "https://github.com/poretsky/ru_tts",
        "Original author": "Igor Poretsky",
    },
    license="MIT",
    packages=find_packages(),
    ext_modules=[pyrutts],
    install_requires=[
        "ru-normalizr>=0.2.0",
    ],
    python_requires=">=3.7",
)
