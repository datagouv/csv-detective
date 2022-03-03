#! /usr/bin/env python3


from setuptools import setup, find_packages

setup(
    name = 'csv_detective',
    version = '0.4.2',
    author = 'Etalab',
    author_email = 'info@data.gouv.fr',
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Information Analysis",
        ],
    description = 'Detect CSV column content',
    keywords = 'CSV data processing encoding guess parser tabular',
    license = 'http://www.fsf.org/licensing/licenses/agpl-3.0.html',
    url = 'https://github.com/etalab/csv_detective',
    data_files = [
        ('share/csv_detective', ['CHANGELOG.md', 'LICENSE.AGPL.txt', 'README.md']),
        ],
    entry_points={
        'console_scripts': [
            'csv_detective=csv_detective.cli:run',
            ],
        },
    extras_require = {
        'test': [
            'nose',
            ],
        },
    include_package_data = True,  # Will read MANIFEST.in
    install_requires = [
        'pandas >= 0.20',
        'chardet >= 3.0',
        'unidecode >= 0.4', 'cchardet'
    ],
    packages = find_packages(),
)
