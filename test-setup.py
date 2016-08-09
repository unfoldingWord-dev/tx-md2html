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
    packages=['obs'],
    long_description='Unit test setup file',
    classifiers=[],
    dependency_links=[
        'git+git://github.com/unfoldingWord-dev/uw_tools.git#egg=uw_tools',
    ],
    install_requires=[
        'markdown',
        'requests',
        'uw_tools'
    ],
    test_suite='tests'
)
