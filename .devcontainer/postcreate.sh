#!/bin/bash
set -e

# Instalar herramientas necesarias
sudo apt-get update
sudo apt-get install -y \
    software-properties-common \
    vim \
    curl \
    wget \
    gnupg2 \
    build-essential \
    zlib1g-dev \
    libssl-dev

# Descargar e instalar Python desde source para las versiones que no están en los repos
PYTHON_VERSIONS=("3.8.18" "3.9.18" "3.10.13" "3.11.8")

for version in "${PYTHON_VERSIONS[@]}"; do
    wget "https://www.python.org/ftp/python/${version}/Python-${version}.tgz"
    tar xzf "Python-${version}.tgz"
    cd "Python-${version}"
    ./configure --enable-optimizations
    make -j $(nproc)
    sudo make altinstall
    cd ..
    rm -rf "Python-${version}" "Python-${version}.tgz"
done

# Instalar pip para cada versión
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.8 get-pip.py
python3.9 get-pip.py
python3.10 get-pip.py
python3.11 get-pip.py
python3.12 get-pip.py


pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements_dev.txt