# -*- coding: utf-8 -*-
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    raise ImportError(
        "Please upgrade `setuptools` to the newest version via: "
        "`pip install -U setuptools`"
    )

if __name__ == "__main__":
    with open('README.md') as fp:
        readme = fp.read()
    with open('requirements.txt') as fp:
        install_requires = [req.strip() for req in fp]
        print 'Install requires:', install_requires

    config = {
        'description': 'Detect CSV column content',
        'author': 'B2OBA',
        'url': 'https://github.com/SGMAP-AGD/csv_detective',
        'author_email': 'NA',
        'namespace_packages':  [],
        'version': '0.1',
        'install_requires': install_requires,
        'tests_require': [],
        'packages':find_packages(),

        # trying to add files...
        'include_package_data':True,
        'package_data':{'': ['*.txt']},

        'scripts': ['bin/csv_detective'],
        'name': 'csv_detective',
        'long_description': readme,
    }
    
    # Write list of all packages in text file
    with open(os.path.join('csv_detective', 'all_packages.txt'), 'wb') as f:
        for x in find_packages():
            f.write(x + '\n')

    setup(**config)