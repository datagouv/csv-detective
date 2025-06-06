from pathlib import Path
from setuptools import setup, find_packages


def pip(filename):
    """Parse pip reqs file and transform it to setuptools requirements."""
    return open(filename).readlines()


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

with open(this_directory / "csv_detective/__init__.py") as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith("__version__"):
            _, _, version = line.replace("'", "").replace('"', "").split()
            break

setup(
    name="csv_detective",
    version=version,
    author="Etalab",
    author_email="opendatateam@data.gouv.fr",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: Information Analysis",
        ],
    description="Detect tabular files column content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="CSV data processing encoding guess parser tabular",
    license="https://spdx.org/licenses/MIT.html#licenseText",
    url="https://github.com/datagouv/csv_detective",
    project_urls={
        "Source": "https://github.com/datagouv/csv_detective",
    },
    data_files=[
        ("share/csv_detective", ["CHANGELOG.md", "LICENSE", "README.md"]),
    ],
    entry_points={
        "console_scripts": [
            "csv_detective=csv_detective.cli:run",
        ],
    },
    python_requires=">=3.9",
    setup_requires=pip("requirements-build.txt"),
    install_requires=pip("requirements.txt"),
    extras_require={
        "dev": pip("requirements-dev.txt"),
    },
    packages=find_packages(),
)
