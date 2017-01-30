from setuptools import setup

setup(
    name="tx-md2html",
    version="0.0.1",
    author="unfoldingWord",
    author_email="unfoldingword.org",
    description="Unit test setup file.",
    license="MIT",
    keywords="",
    url="https://github.org/unfoldingWord-dev/tx-md2html",
    long_description='Unit test setup file',
    classifiers=[],
    install_requires=[
        'markdown==2.6.7',
        'requests==2.13.0',
        'uw_tools==0.0.6',
        'setuptools==12.0.5',
        'bs4==0.0.1'
    ],
    test_suite='tests'
)
