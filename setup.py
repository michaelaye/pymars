import ez_setup
ez_setup.use_setuptools()
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-v', '-m', 'not luna']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


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
