#!/usr/bin/env python

from distutils.core import setup

setup(name='PDSImage',
      version='1.0',
      description='NASA PDS single-band image support',
      author='Michael Bentley',
      author_email='michael@jedimindworks.com',
      url='http://pdsimagereader.sourceforge.net',
      py_modules=['PDSImage'],
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'License :: OSI Approved :: Python Software Foundation License',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Topic :: Multimedia :: Graphics :: Graphics Conversion',  
            'Topic :: Scientific/Engineering',  
            'Topic :: Software Development :: Libraries :: Python Modules']
     )
