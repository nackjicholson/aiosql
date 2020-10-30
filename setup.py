from setuptools import setup, find_packages
from pathlib import Path
import re

DIR = Path(__file__).parent

with open(DIR / "README.md", "r") as fh:
    long_description = fh.read()

def extract(prop, text):
    return re.search(f"{prop} = \"(.*)\"", text).group(1)

with open(DIR / "pyproject.toml") as ph:
    text = ph.read()
    name = extract("name", text)
    version = extract("version", text)
    url = extract("repository", text)
    description = extract("description", text)

assert name is not None and version is not None and \
    url is not None and description is not None

setup(
    name=name,
    version=version,
    packages=find_packages(),
    author="William Vaughn",
    author_email="vaughnwilld@gmail.com",
    url=url,
    install_requires=[],
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: SQL",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
