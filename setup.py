import os
from pathlib import Path

from Cython.Build import cythonize
from setuptools import Extension, setup
from setuptools.command.build_py import build_py as _build_py

SRC_ROOT = Path(__file__).parent / "src"


def iter_compile_modules():
  for py in SRC_ROOT.rglob("*.py"):
    if py.name != "__init__.py":
      yield py


COMPILE_MODULES = list(iter_compile_modules())
COMPILE_PY_ABS = {os.path.abspath(str(py)) for py in COMPILE_MODULES}


def py_to_module_name(py: Path) -> str:
  return ".".join(py.relative_to(SRC_ROOT).with_suffix("").parts)


class build_py(_build_py):
  def find_package_modules(self, package, package_dir):
    modules = super().find_package_modules(package, package_dir)
    return [
      (pkg, mod, file)
      for pkg, mod, file in modules
      if os.path.abspath(file) not in COMPILE_PY_ABS
    ]


setup(
  ext_modules=cythonize(
    [Extension(py_to_module_name(py), [str(py)]) for py in COMPILE_MODULES],
    language_level="3",
    compiler_directives={"binding": True},
    build_dir="build/cython",
  ),
  package_data={
    "": ["*.pyi", "py.typed"],
  },
  cmdclass={"build_py": build_py},
)
