import sys
from setuptools import setup, find_packages

setup(
    name = "pymars",
    version = "2.7.0beta1",
    packages = find_packages(),

    install_requires = ['cliutils'],
    tests_require = ['pytest'],

    cmdclass = {'test': PyTest},

    entry_points={
        "console_scripts": [
            'get_Ls = pymars.kmaspice:get_current_l_s'
            ]
    },

    #metadata
    author = "K.-Michael Aye",
    author_email = "kmichael.aye@gmail.com",
    description = "Software for analysing HiRISE and other Mars data.",
    license = "BSD 2-clause",
    keywords = "Mars HiRISE MOLA CTX",
    url = "",
)
