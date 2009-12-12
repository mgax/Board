from setuptools import setup, find_packages

setup(
    name="Board",
    version="0.1",
    url="http://github.com/alex-morega/Board",
    license="BSD License",
    author="Alex Morega",
    author_email="public@grep.ro",
    packages=find_packages(),
    setup_requires=['nose>=0.11'],
    install_requires=['zope.component'],
    test_suite="nose.collector",
#    entry_points={
#        'console_scripts': [
#            'bd = board.cmd:main',
#        ],
#    },
)
