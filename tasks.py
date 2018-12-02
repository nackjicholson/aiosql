from invoke import task
from pathlib import Path
from shutil import rmtree

root_path = Path(__file__).parent
package_dir = root_path / "aiosql"
docs_dir = root_path / "docs"
source_dir = docs_dir / "source"
build_dir = docs_dir / "_build"


@task
def docs(c):
    if source_dir.exists():
        rmtree(source_dir)
    if build_dir.exists():
        rmtree(build_dir)
    c.run(f"sphinx-apidoc -f -e -o {source_dir} {package_dir}")
    c.run(f"sphinx-build -M html {docs_dir} {build_dir}")
