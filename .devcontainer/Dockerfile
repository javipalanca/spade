FROM ubuntu:22.04

# Instalar versiones de Python 3.9, 3.10, 3.11 y 3.12
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.9 python3.10 python3.11 python3.12 \
    && apt-get install -y python3-pip \
    # Instalar distutils y setuptools para todas las versiones de Python
    && apt-get install -y python3-distutils python3-setuptools \
    && apt-get install -y python3.9-distutils python3.10-distutils python3.11-distutils python3.12-distutils \
    && apt-get install -y python3.9-dev python3.10-dev python3.11-dev python3.12-dev

# establecer Python 3.12 como predeterminado
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 2 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 3 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 4

# Actualizar pip y setuptools
RUN pip install --upgrade pip setuptools wheel

# Instalar tox
RUN pip install tox

# Establecer directorio de trabajo
WORKDIR /workspaces/spade

# No copiar requirements.txt (esto se hará después del montaje)
# Los archivos se montarán automáticamente desde tu directorio local

# Establecer Python 3.12 como predeterminado
ENV PYTHONPATH=/workspaces/spade