from setuptools import setup

setup(
    name="tx-md2html",
    version="0.0.2",
    author="unfoldingWord",
    author_email="unfoldingword.org",
    description="Unit test setup file.",
    license="MIT",
    keywords="",
    url="https://github.org/unfoldingWord-dev/tx-md2html",
    long_description='Unit test setup file',
    classifiers=[],
    dependency_links=[
        'git+git://github.com/unfoldingWord-dev/tx-manager.git@develop#egg=tx-manager',
    ],
    install_requires=[
        'markdown',
        'requests',
        'bs4',
        'tx-manager'
    ],
    test_suite='tests'
)
