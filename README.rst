HIT-MAP
=======

**High-throughput Integrated Tagging for cell MAPping (HIT-MAP)** is an efficient end-to-end pipeline for massively parallel endogenous protein tagging, coupled to accelerated multi-modal acquisition of protein spatial imaging and biophysical interaction data.

- **Free software**: MIT license
- **Documentation**: https://hit-map.readthedocs.io
- **Source code**: https://github.com/idekerlab/hit_map


Installation
============

STEP 0: Setup Running Environment
---------------------------------

Option 1: Local Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This repository requires the following Python packages::

    cellmaps_pipeline
    networkx
    scipy
    tqdm
    phenograph
    numpy
    torch
    pandas
    matplotlib
    dill
    multipagetiff

Create a file named ``requirements.txt`` with the above list, then install via::

    pip install -r requirements.txt

Additionally, install **deconwolf** (https://elgw.github.io/deconwolf/), which is written in C.
Follow the official installation instructions on their website.

Option 2: Run via Docker
~~~~~~~~~~~~~~~~~~~~~~~~

A Dockerfile is provided to build a reproducible environment. Example::

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
     && printf "/usr/local/lib\n" > /etc/ld.so.conf.d/usrlocal.conf \
     && ldconfig

    # ---- Python deps for your CLI and runner ----
    RUN python3 -m pip install --upgrade pip \
     && python3 -m pip install \
        numpy pandas scipy matplotlib \
        opencv-python-headless \
        multipagetiff \
        cellmaps-utils \
        fairscape-cli

    WORKDIR /work

    # No ENTRYPOINT so you can choose: python, dw, dw_bw, or bash at runtime

Running
=======

Setup Input
-----------

Input includes **wide-field images** and **AP-MS PPI files**.

Images
~~~~~~

Organize images into a folder with four subfolders::

    image_folder/
    ├── blue      # nucleus
    ├── green     # protein of interest
    ├── red       # mitochondria
    └── yellow    # ER

Metadata
~~~~~~~~

An ``image_meta.tsv`` file is required with the following fields:

- ``file_directory``: path to image directory
- ``channel``: mapping of channels (blue: nucleus, green: targeted protein, red: microtubule, yellow: ER)
- ``targeted_proteins``: protein(s) of interest
- ``save_prefix``: prefix for saved files

Microscope Setup
~~~~~~~~~~~~~~~~

A ``microscope_setup_param.npy`` file is required with a dictionary containing:

- ``ni``: refractive index (float)
- ``NA``: numerical aperture (float)
- ``lambda``: wavelength dictionary ``{blue:int, red:int, green:int, yellow:int}``
- ``resxy``: pixel size (int)
- ``resz``: distance between panels (int)
- ``threads``: multiprocessing threads (int)

PPI Data
~~~~~~~~

A ``PPI_folder`` containing ``ppi_file.tsv`` with filtered high-confidence PPIs.


Command Line Running
--------------------

Run::

    python hit_mapcmd.py \
      --image_meta /path/to/image_meta.tsv \
      --ppi_dir /path/to/ppi_file.tsv \
      --microscope_setup_param /path/to/microscope_setup_param.npy \
      --output_dir /path/to/save/outputfiles

Provenance
~~~~~~~~~~

By default, provenance files are taken from::

    ./hit_map/provence_files/provence_image.json
    ./hit_map/provence_files/provence_ppi.json

You may edit these files manually for FAIR compliance or provide custom files via::

    --provenance_img
    --provenance_ppi

Output Files
------------

All results will be stored under the specified ``output_dir``:

- **deconvoluted_images/**: deconvolved ``.tif`` images (PSF corrected)
  - subfolders: blue, green, red, yellow

- **z_max_projection/**: Z-max projected ``.jpg`` images
  - subfolders: blue, green, red, yellow

- **embedding/**: data embeddings
  - ``img_embedding/``: ``img_emb.tsv`` (image embeddings capturing protein localization)
  - ``ppi_embedding/``: ``ppi_emb.tsv`` (PPI network embeddings)
  - ``co_embedding/``: ``co_emb.tsv`` (joint protein embedding space)

- **hierarchy/**: ``.cx2`` file of co-embedded hierarchy clustered using HiDef

- **hierarchy_eval/**: evaluation results (enrichment against HPA, GO, CORUM, etc.)


License
=======

This project is licensed under the **MIT License**. See the ``LICENSE`` file for details.


Contributing
============

Contributions, issues, and feature requests are welcome.
Please open an issue or submit a pull request to collaborate.


Authors
=======

Developed and maintained by the **Ideker Lab**.


Compatibility
=============

- Python 3.8 to Python 3.11


Usage
=====

For information, invoke::

    hit_mapcmd.py -h


Credits
=======

This package was created with `Cookiecutter <https://github.com/audreyr/cookiecutter>`_ and the `audreyr/cookiecutter-pypackage <https://github.com/audreyr/cookiecutter-pypackage>`_ project template.

- `NDEx <http://www.ndexbio.org>`_
