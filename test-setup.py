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
        'https://github.com/unfoldingWord-dev/tx-manager/tarball/develop#egg=tx-manager',
    ],
    install_requires=[
        'markdown',
        'requests==2.13.0',
        'uw_tools==0.0.6',
        'bs4',
        'tx-manager'
    ],
    test_suite='tests'
)
