HIT-MAP
=======

**High-throughput Integrated Tagging for cell MAPping (HIT-MAP)** is an efficient end-to-end pipeline for massively parallel endogenous protein tagging, coupled to accelerated multi-modal acquisition of protein spatial imaging and biophysical interaction data.

- **Free software**: MIT license
- **Documentation**: https://hit-map.readthedocs.io
- **Source code**: https://github.com/idekerlab/hit_map


Installation
============

Setup Running Environment
---------------------------------

Option 1: Local Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This repository requires the following Python packages::

    cellmaps_pipeline
    os
    shutil
    time
    subprocess
    cv2
    multipagetiff
    numpy
    pandas
    cellmaps_utils

Create a file named ``requirements.txt`` with the above list, then install via::

    pip install -r requirements.txt

Additionally, install **deconwolf** (https://elgw.github.io/deconwolf/), which is written in C.
Follow the official installation instructions on their website.

Option 2: Run via Docker
~~~~~~~~~~~~~~~~~~~~~~~~

A Dockerfile is provided to build a reproducible environment. It can be found in ``docker/Dockerfile`` in this repo.

Clone repo and build the docker image::

    git clone git@github.com:idekerlab/hit_map.git
    cd hit_map
    docker build -f docker/Dockerfile -t hitmap:latest .

Run::

    docker run --rm -it \                              
      -v "$(pwd)":/work -w /work \
      hitmap:latest \
      python3 -m hit_map.hit_mapcmd \
        --image_meta /work/tests/image_meta.tsv \
        --ppi_dir /work/tests/PPI_folder \
        --microscope_setup_param /work/tests/microscope_setup_param.npy \
        --psigma 2.0 \
        --provenance_img /work/hit_map/provenance_files/provenance_image.json \
        --provenance_ppi /work/hit_map/provenance_files/provenance_ppi.json \
        --outdir /work/mydir2 --generate_hierarchy

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
