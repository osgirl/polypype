from codecs import open
from setuptools import setup, find_packages
from os import path


with open(path.join(path.abspath(path.dirname(__file__)),
                    'README.rst'), encoding='utf-8') as readme_file:
    long_description = readme_file.read()

setup(
    name='polypype',
    version='0.1.0',
    description='A python library for writing polypipe events to a file',
    long_description=long_description,
    url='https://github.com/dan-f/polypype',
    author='Daniel Friedman',
    author_email='dfriedman58@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    keywords='polypype polypipe soundpipe audio sound events midi',
    packages=find_packages(exclude=['*.tests']),
    extras_require={
        'test': ['pytest', 'unittest2', 'ddt', 'mock', 'pylint', 'pep8']
    }
)
