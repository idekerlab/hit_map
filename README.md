# HIT-MAP

**High-throughput Integrated Tagging for cell MAPping (HIT-MAP)** is an efficient end-to-end pipeline for massively parallel endogenous protein tagging, coupled to accelerated multi-modal acquisition of protein spatial imaging and biophysical interaction data.

- **Free software**: MIT license  
- **Documentation**: [https://hit-map.readthedocs.io](https://hit-map.readthedocs.io)  
- **Source code**: [https://github.com/idekerlab/hit_map](https://github.com/idekerlab/hit_map)  

---

## 🛠 Installation

### STEP 0: Setup Running Environment

#### Option 1: Local Installation

This repository requires the following Python packages:

```txt
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
```

📌 Create a file named `requirements.txt` with the above list, then install via:

```bash
pip install -r requirements.txt
```

Additionally, install **[deconwolf](https://elgw.github.io/deconwolf/)**, which is written in C.  
Follow the official installation instructions on their website.

---

#### Option 2: Run via Docker

A Dockerfile is provided to build a reproducible environment. Example:

```dockerfile
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# install deps
RUN apt-get update && apt-get install -y --no-install-recommends     ca-certificates build-essential cmake pkg-config git     libfftw3-dev libgsl-dev libomp-dev libpng-dev libtiff-dev  && update-ca-certificates  && rm -rf /var/lib/apt/lists/*

# build & install deconwolf
RUN git clone https://github.com/elgw/deconwolf.git /opt/deconwolf  && cd /opt/deconwolf && mkdir build && cd build  && cmake -DENABLE_GPU=OFF -DENABLE_NATIVE_OPTIMIZATION=ON ..  && cmake --build . --config Release -j"$(nproc)"  && cmake --install .  && printf "/usr/local/lib\n" > /etc/ld.so.conf.d/usrlocal.conf  && ldconfig
```

---
##  🤸‍♀️🤸‍♀Running 
### STEP 1: Clone the Repository

```bash
git clone https://github.com/idekerlab/hit_map
cd hit_map
pip install -r requirements_dev.txt
make install
```

---

### STEP 2: Setup Input

Input includes **wide-field images** and **AP-MS PPI files**.

#### Images

Organize images into a folder with four subfolders:

```txt
image_folder/
├── blue      # nucleus
├── green     # protein of interest
├── red       # mitochondria
└── yellow    # ER
```

#### Metadata

An `image_meta.tsv` file is required with the following fields:

- `file_directory`: path to image directory  
- `channel`: mapping of channels (blue: nucleus, green: targeted protein, red: microtubule, yellow: ER)  
- `targeted_proteins`: protein(s) of interest  
- `save_prefix`: prefix for saved files  

#### Microscope Setup

A `microscope_setup_param.npy` file is required with a dictionary containing:

- `ni`: refractive index (float)  
- `NA`: numerical aperture (float)  
- `lambda`: wavelength dictionary `{blue:int, red:int, green:int, yellow:int}`  
- `resxy`: pixel size (int)  
- `resz`: distance between panels (int)  
- `threads`: multiprocessing threads (int)  

#### PPI Data

A `PPI_folder` containing `ppi_file.tsv` with filtered high-confidence PPIs.

---

### STEP 3: Command Line Running

```bash
python hit_mapcmd.py   --image_meta /path/to/image_meta.tsv   --ppi_dir /path/to/ppi_file.tsv   --microscope_setup_param /path/to/microscope_setup_param.npy   --output_dir /path/to/save/outputfiles
```

#### Provenance

By default, provenance files are taken from:

```txt
./hit_map/provence_files/provence_image.json
./hit_map/provence_files/provence_ppi.json
```

You may edit these files manually for FAIR compliance or provide custom files via:

```txt
--provenance_img
--provenance_ppi
```

---

### STEP 4: Output Files

All results will be stored under the specified `output_dir`:

- **deconvoluted_images/**: deconvolved `.tif` images (PSF corrected)  
  - subfolders: blue, green, red, yellow  

- **z_max_projection/**: Z-max projected `.jpg` images  
  - subfolders: blue, green, red, yellow  

- **embedding/**: data embeddings  
  - `img_embedding/`: `img_emb.tsv` (image embeddings capturing protein localization)  
  - `ppi_embedding/`: `ppi_emb.tsv` (PPI network embeddings)  
  - `co_embedding/`: `co_emb.tsv` (joint protein embedding space)  

- **hierarchy/**: `.cx2` file of co-embedded hierarchy clustered using HiDef  

- **hierarchy_eval/**: evaluation results (enrichment against HPA, GO, CORUM, etc.)  

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Contributing

Contributions, issues, and feature requests are welcome.  
Please open an issue or submit a pull request to collaborate.

---

## 👩‍💻 Authors

Developed and maintained by the **Ideker Lab**. 


# Compatibility

- Python 3.8+

# Installation

```bash
git clone https://github.com/idekerlab/hit_map
cd hit_map
pip install -r requirements_dev.txt
make install
```

Run the `make` command with no arguments to see other build/deploy options including creation of a Docker image:

```bash
make
```

**Output:**

```
clean                remove all build, test, coverage and Python artifacts
clean-build          remove build artifacts
clean-pyc            remove Python file artifacts
clean-test           remove test and coverage artifacts
lint                 check style with flake8
test                 run tests quickly with the default Python
test-all             run tests on every Python version with tox
coverage             check code coverage quickly with the default Python
docs                 generate Sphinx HTML documentation, including API docs
servedocs            compile the docs watching for changes
testrelease          package and upload a TEST release
release              package and upload a release
dist                 builds source and wheel package
install              install the package to the active Python's site-packages
dockerbuild          build docker image and store in local repository
dockerpush           push image to dockerhub
```

# Usage

For information, invoke:

```bash
hit_mapcmd.py -h
```

**Example usage**

> **TODO:** Add information about example usage

```bash
hit_mapcmd.py # TODO Add other needed arguments here
```

# For Developers

⚠️ Note: Commands below assume you’ve already run:

```bash
pip install -r requirements_dev.txt
```

## Run Tests

To run unit tests:

```bash
make test
```

## Make Documentation

Documentation is stored under `docs/` and can be published on [Read the Docs](https://readthedocs.io).

Install additional dependencies:

```bash
pip install -r docs/requirements.txt
```

Build the docs locally:

```bash
make docs
```

This will create HTML documentation under `docs/_build/html` and open it in your default browser.

## Deploy Development Versions

Steps to make changes, deploy, and run against them:

1. **Make changes**  
   Modify code in this repo as desired.

2. **Build and deploy**

   ```bash
   # From base directory of this repo (hit_map)
   pip uninstall hit_map -y
   make clean dist
   pip install dist/hit_map*whl
   ```

# Needed Files

> **TODO:** Add description of needed files

# Via Docker

**Example usage**

> **TODO:** Add information about example usage

```bash
Coming soon ...
```

# Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.

- [NDEx](http://www.ndexbio.org)

