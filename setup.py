# -*- coding: utf-8 -*-

"""The setup script."""
import subprocess
import sys
from setuptools import setup, find_packages


def parse_requirements(filename):
    """load requirements from a pip requirements file"""
    with open(filename) as f:
        lineiter = [line.strip() for line in f]
    return [line for line in lineiter if line and not line.startswith("#")]


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = parse_requirements("requirements.txt")

if sys.platform.startswith("win32"):
    requirements.append("winloop>=0.1.7")
else:
    requirements.append("uvloop>=0.21.0")

setup_requirements = [
    "pytest-runner",
    # put setup requirements (distutils extensions, etc.) here
]

test_requirements = parse_requirements("requirements_dev.txt")


"""
Check for a slixmpp installation in the current env.
The slixmpp-multiplatform dependency generates conflicts with any previous slixmpp installation.
You should use SPADE in an isolated environment (venv, conda, docker...)
"""
subprocess.call([sys.executable, "-m", "pip", "uninstall", "-y", "slixmpp"])


setup(
    name="spade",
    version="4.1.2",
    description="Smart Python Agent Development Environment",
    long_description=readme + "\n\n" + history,
    author="Javi Palanca",
    author_email="jpalanca@gmail.com",
    url="https://spadeagents.eu",
    packages=find_packages(include=["spade"]),
    entry_points={"console_scripts": ["spade=spade.cli:cli"]},
    include_package_data=True,
    package_data={"spade": ["templates"]},
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords="spade",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: XMPP",
    ],
    test_suite="tests",
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
