FROM ubuntu:22.04


ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---- OS deps (build tools, certs, and libs for TIFF/OpenMP/OpenCV) ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git \
    build-essential cmake pkg-config \
    python3 python3-pip python3-venv \
    libfftw3-dev libgsl-dev libomp-dev libpng-dev libtiff-dev \
    libglib2.0-0 libgl1 \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# ---- Build & install Deconwolf (CPU) ----
ARG DW_REF=v0.4.2
RUN git clone https://github.com/elgw/deconwolf.git /opt/deconwolf \
 && cd /opt/deconwolf && git checkout "${DW_REF}" || true \
 && mkdir -p /opt/deconwolf/build && cd /opt/deconwolf/build \
 && cmake -DENABLE_GPU=OFF -DENABLE_NATIVE_OPTIMIZATION=ON .. \
 && cmake --build . --config Release -j"$(nproc)" \
 && cmake --install . \
 # ensure runtime linker can find /usr/local/lib (for libtrafo.so etc)
 && printf "/usr/local/lib\n" > /etc/ld.so.conf.d/usrlocal.conf \
 && ldconfig

 # ---- Install igraph + leidenalg (with modern build toolchain) ----
# 1) Make sure we have Python headers & modern setuptools/wheel in the build env
RUN apt-get update && apt-get install -y --no-install-recommends python3-dev && rm -rf /var/lib/apt/lists/* \
 && python3 -m pip install --upgrade "setuptools>=70" "wheel>=0.43" "setuptools-scm>=8" "pybind11>=2.10"

# 2) Try to use wheels for igraph (most aarch64 images have them)
RUN python3 -m pip install "igraph>=0.11,<0.12" \
 # 3) Build/install leidenalg using our upgraded toolchain (no isolated old setuptools)
 && python3 -m pip install --no-build-isolation "leidenalg==0.9.1"

# ---- Python deps for your CLI and runner ----
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install \
    numpy pandas scipy matplotlib \
    opencv-python-headless \
    multipagetiff \
    cellmaps-utils \
    fairscape-cli \
    cellmaps-image-embedding==0.3.3 \
    cellmaps-ppi-embedding==0.4.3 \
    cellmaps-coembedding==1.4.0 \
    cellmaps-generate-hierarchy==0.2.4 \
    cellmaps-hierarchyeval==0.2.2

# Workdir where you’ll mount your repo + data
WORKDIR /work

# Add symlinks for fairscape and hidef to /usr/bin since ENV PATH
# does not seem to be working 
RUN ln -s /usr/local/bin/fairscape-cli /usr/bin/fairscape-cli
RUN ln -s /usr/local/bin/hidef_finder.py /usr/bin/hidef_finder.py

# No ENTRYPOINT so you can choose: python, dw, dw_bw, or bash at runtime
