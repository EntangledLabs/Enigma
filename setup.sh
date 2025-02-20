#!/bin/bash

# Updates
apt update
apt dist-upgrade -y
apt autoremove

# Install dependencies
apt install build-essential gdb lcov pkg-config \
      libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
      libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
      lzma lzma-dev tk-dev uuid-dev zlib1g-dev curl git

# Install Python 3.13.2
curl -L -O https://www.python.org/ftp/python/3.13.2/Python-3.13.2.tgz
tar -xf Python-3.13.2.tgz

cd Python-3.13.2

./configure --enable-optimizations

make
make altinstall

cd ..

git clone https://github.com/EntangledLabs/Enigma.git
