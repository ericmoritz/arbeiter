from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='arbeiter',
      version=version,
      description="An unassuming work queue system",
      long_description="""\
A work queue system built using Kestrel""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Eric Moritz',
      author_email='eric@themoritzfamily.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
        "pykestrel",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
