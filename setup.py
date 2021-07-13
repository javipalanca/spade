# -*- coding: utf-8 -*-

"""The setup script."""
from setuptools import setup, find_packages


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = parse_requirements("requirements.txt")

setup_requirements = [
    'pytest-runner',
    # put setup requirements (distutils extensions, etc.) here
]

test_requirements = parse_requirements("requirements_dev.txt")

setup(
    name='spade',
    version='3.2.0',
    description="Smart Python Agent Development Environment",
    long_description=readme + '\n\n' + history,
    author="Javi Palanca",
    author_email='jpalanca@gmail.com',
    url='https://github.com/javipalanca/spade',
    packages=find_packages(include=['spade']),
    entry_points={
        'console_scripts': [
            'spade=spade.cli:main'
        ]
    },
    include_package_data=True,
    package_data={"spade": ["templates"]},
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='spade',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Internet :: XMPP',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
