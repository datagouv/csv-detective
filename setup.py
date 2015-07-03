try:
    from setuptools import setup
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
        'packages': [
            'csv_detective'
        ],
        'scripts': ['bin/csv_detective'],
        'name': 'csv_detective',
        'long_description': readme,
    }

    setup(**config)
