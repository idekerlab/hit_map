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
    libglib2.0-0 \
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

# ---- Python deps for your CLI and runner ----
# (opencv-python-headless avoids GUI deps)
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install \
      numpy \
      pandas \
      scipy \
      matplotlib \
      multipagetiff \
      opencv-python-headless \
      cellmaps-utils \
      fairscape-cli \
      cellmaps_pipeline
WORKDIR /work
# No ENTRYPOINT so you can choose: python, dw, dw_bw, or bash at runtime
