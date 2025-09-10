#!/usr/bin/env python

import logging
import os
import shutil
import time
import subprocess
import sys

import cv2
import hit_map
import multipagetiff as mtif
import numpy as np
import pandas as pd
from cellmaps_utils import logutils
from cellmaps_utils.provenance import ProvenanceUtil
from hit_map.exceptions import HitmapError

logger = logging.getLogger(__name__)


class HitmapRunner(object):
    """
    Class to run algorithm
    """

    def __init__(
        self,
        image_meta=None,
        ppi_dir=None,
        microscope_setup_param=None,
        psigma=None,
        outdir=None,
        provenance_img=None,
        provenance_ppi=None,
        generate_hierarchy=True,
        iteration=100,
        k = None,
        exitcode=None,
        skip_logging=True,
        input_data_dict=None,
        provenance_utils=ProvenanceUtil(),
    ):
        """
        Constructor

        :param outdir: Directory to create and put results in
        :type outdir: str
        :param skip_logging: If ``True`` skip logging, if ``None`` or ``False`` do NOT skip logging
        :type skip_logging: bool
        :param exitcode: value to return via :py:meth:`.HitmapRunner.run` method
        :type int:
        :param input_data_dict: Command line arguments used to invoke this
        :type input_data_dict: dict
        :param provenance_utils: Wrapper for `fairscape-cli <https://pypi.org/project/fairscape-cli>`__
                                 which is used for
                                 `RO-Crate <https://www.researchobject.org/ro-crate>`__ creation and population
        :type provenance_utils: :py:class:`~cellmaps_utils.provenance.ProvenanceUtil`
        """
        if outdir is None:
            raise HitmapError("outdir is None")
        self.image_meta = image_meta
        self.ppi_dir = ppi_dir
        self.microscope_setup_param = np.load(microscope_setup_param, allow_pickle=True).item()
        self.psigma = psigma
        self.provenance_img = provenance_img
        self.provenance_ppi = provenance_ppi
        self.generate_hierarchy = generate_hierarchy
        self.iteration = iteration
        self.k = k
        self._outdir = os.path.abspath(outdir)

        self._exitcode = exitcode
        self._start_time = int(time.time())
        if skip_logging is None:
            self._skip_logging = False
        else:
            self._skip_logging = skip_logging
        self._input_data_dict = input_data_dict
        self._provenance_utils = provenance_utils

        logger.debug("In constructor")

    # ### Image deconvolution functions
    def generate_theoretical_PSF(self, ni, NA, lamb, resxy, resz, save_dir, threads=4):
        """
        Need to install deconwolf/0.4.2

        :param ni: refractive index
        :param NA: numerical aperture
        :param lamb: wavelength
        :param resxy: pixel size
        :param resz: destance between panels
        :param save_dir: output file with name and directory
        :param threads: integer, for multiprocessing
        """
        subprocess.run([
            "dw_bw",
            "--ni", str(ni),
            "--NA", str(NA),
            "--lambda", str(lamb),
            "--resxy", str(resxy),
            "--resz", str(resz),
            "--threads", str(threads),
            save_dir], check=True)


    def format_deconwolf(self, image_dir, psf_dir, psigma, save_prefix, iteration):
        subprocess.run([
            "dw",
            "--iter", str(iteration),
            image_dir,
            psf_dir,
            "--psigma", str(psigma),
            "--prefix", str(save_prefix)], check=True)
    def z_max_projection(self, img_stack, channel=0):
        # channel 0 is default channel to stack
        return np.max(img_stack, axis=channel)

    def enhance_contrast(self, img, saturation_level=0.7):
        clahe = cv2.createCLAHE(clipLimit=saturation_level, tileGridSize=(8, 8))
        enhanced_L = clahe.apply(img)
        return enhanced_L

    def z_projection(self, image_dir, save_dir, dz=1, dx=1):
        for image in os.listdir(image_dir):
            if image.endswith(".tif"):
                stack = mtif.read_stack(f"{image_dir}/{image}", dx=dx, dz=dz, units="nm")
                stack = stack.pages
                z_max = self.z_max_projection(stack)
                image_8bit = cv2.normalize(z_max, None, 0, 255, cv2.NORM_MINMAX).astype("uint8")
                z_max = self.enhance_contrast(image_8bit)
                save_name = "_".join(image.split("_"))[:-4] + "_" + f"{image_dir.split('/')[-1]}" + ".jpg"
                cv2.imwrite(f"{save_dir}/{save_name}", z_max)
            else:
                suffix = image_dir.split(".")[-1]
                raise TypeError(f"Expect .tif images, but got .{suffix}")

    def generate_node_attribute(self, input_dir, save_dir):
        filename = []
        name = []
        for file in os.listdir(f"{input_dir}/blue"):
            if file.endswith(".jpg"):
                filename.append("_".join(file.split("_")[:-1]) + "_")
                name.append(file.split("_")[1]) ### name of the gene
        df = pd.DataFrame({"name": name, "filename": filename})
        df.to_csv(f"{save_dir}/1_image_gene_node_attributes.tsv", sep="\t", index=False)

    def cellmaps_image_embedding(self, image_dir, provenance, outdir):
        subprocess.run([
            sys.executable, "-m", "cellmaps_image_embedding.cellmaps_image_embeddingcmd",
            outdir, "--inputdir", image_dir, "--provenance", provenance
        ], check=True)

    def cellmaps_PPI_embedding(self, ppi_score_file, provenance, outdir):
        subprocess.run([
            sys.executable, "-m", "cellmaps_ppi_embedding.cellmaps_ppi_embeddingcmd",
            outdir, "--inputdir", ppi_score_file, "--provenance", provenance
        ], check=True)

    def cellmaps_co_embedding(self, image_embedding_dir, ppi_embedding_dir, outdir, k):
        subprocess.run([
            sys.executable, "-m", "cellmaps_coembedding.cellmaps_coembeddingcmd",
            outdir, "--embeddings", image_embedding_dir, ppi_embedding_dir, "--k", str(k)
        ], check=True)



    def cellmaps_generate_hierarchy(self, co_embedding_dir, out_dir):
        
        subprocess.run([
            sys.executable, "-m", "cellmaps_generate_hierarchy.cellmaps_generate_hierarchycmd",
            out_dir, "--coembedding_dirs", co_embedding_dir
        ], check=True)

    def cellmaps_hierarchyeval(self, hierarchy_dir, outdir):
        subprocess.run([
            sys.executable, "-m", "cellmaps_hierarchyeval.cellmaps_hierarchyevalcmd",
            outdir, "--hierarchy_dir", hierarchy_dir
        ], check=True)

    def run(self):
        """
        Runs HIT-MAP

        :return:
        """
        "image meta file with the following columns"
        "file_directory: image direcotry"
        "channel: blue: nucleus, green: targeted protein,red: microtubule yellow:ER"
        "targetted_proteins: targetting protein of interest "
        "save_prefix: save file prefix"

        exitcode = 99
        try:
            logger.debug("In run method")
            if os.path.isdir(self._outdir):
                raise HitmapError(self._outdir + " already exists")
            if not os.path.isdir(self._outdir):
                os.makedirs(self._outdir, mode=0o755)
            if self._skip_logging is False:
                logutils.setup_filelogger(outdir=self._outdir, handlerprefix="hit_map")
            logutils.write_task_start_json(
                outdir=self._outdir,
                start_time=self._start_time,
                data={"commandlineargs": self._input_data_dict},
                version=hit_map.__version__,
            )

            # ### Generate the psf files
            for key, value in self.microscope_setup_param["lambda"].items():
                if not os.path.isdir(f"{self._outdir}/theoretical_psf"):
                    os.makedirs(f"{self._outdir}/theoretical_psf", mode=0o755)

                self.generate_theoretical_PSF(
                    self.microscope_setup_param["ni"],
                    self.microscope_setup_param["NA"],
                    value,
                    self.microscope_setup_param["resxy"],
                    self.microscope_setup_param["resz"],
                    f"{self._outdir}/theoretical_psf/{key}_psf.tiff",
                    threads=self.microscope_setup_param["threads"],
                )
            print("Successfully generated theoretical PSF.")

            # ### Image deconvolution
            image_meta = pd.read_csv(self.image_meta, sep="\t")
            if not os.path.isdir(f"{self._outdir}/deconvoluted_images"):
                os.makedirs(f"{self._outdir}/deconvoluted_images", mode=0o755)
            if not os.path.isdir(f"{self._outdir}/deconvoluted_images/blue"):
                os.makedirs(f"{self._outdir}/deconvoluted_images/blue", mode=0o755)
            if not os.path.isdir(f"{self._outdir}/deconvoluted_images/red"):
                os.makedirs(f"{self._outdir}/deconvoluted_images/red", mode=0o755)
            if not os.path.isdir(f"{self._outdir}/deconvoluted_images/green"):
                os.makedirs(f"{self._outdir}/deconvoluted_images/green", mode=0o755)
            if not os.path.isdir(f"{self._outdir}/deconvoluted_images/yellow"):
                os.makedirs(f"{self._outdir}/deconvoluted_images/yellow", mode=0o755)
            if not os.path.isdir(f"{self._outdir}/deconvoluted_logs"):
                os.makedirs(f"{self._outdir}/deconvoluted_logs", mode=0o755)
            for i in image_meta.index.values:

                self.format_deconwolf(
                    image_meta.at[i, "file_directory"],
                    f"{self._outdir}/theoretical_psf/{image_meta.at[i, 'channel']}_psf.tiff",
                    self.psigma,
                    image_meta.at[i, "save_prefix"],
                    iteration=self.iteration,
                )


                fd       = image_meta.at[i, 'file_directory']   # full path from the CSV
                prefix   = image_meta.at[i, 'save_prefix']
                channel  = image_meta.at[i, 'channel']
                base     = os.path.basename(fd)                  # just the filename

                src = f"{'/'.join(fd.split('/')[:-1])}/{prefix}_{fd.split('/')[-1]}"

                dst_dir = os.path.join(self._outdir, 'deconvoluted_images', str(channel))
                os.makedirs(dst_dir, exist_ok=True)
                dst = os.path.join(dst_dir, f"{prefix}_{base}")

                # Move the deconvolved file
                shutil.move(src, dst)

                # Move the log file
                log_src = f"{src}.log.txt"
                log_dir = os.path.join(self._outdir, 'deconvoluted_logs')
                os.makedirs(log_dir, exist_ok=True)
                log_dst = os.path.join(log_dir, f"{channel}_{prefix}_{base}.log.txt")
                shutil.move(log_src, log_dst)

            # ### check the deconvolution output
            all_items = os.listdir(f"{self._outdir}/deconvoluted_images/yellow")
            print(f"{self._outdir}/deconvoluted_images/yellow: {len(all_items)}")
            all_items = os.listdir(f"{self._outdir}/deconvoluted_images/green")
            print(f"{self._outdir}/deconvoluted_images/green: {len(all_items)}")
            all_items = os.listdir(f"{self._outdir}/deconvoluted_images/red")
            print(f"{self._outdir}/deconvoluted_images/red: {len(all_items)}")
            all_items = os.listdir(f"{self._outdir}/deconvoluted_images/blue")
            print(f"{self._outdir}/deconvoluted_images/blue: {len(all_items)}")

            # ### Deconvolution images z_max projection and enhancing
            if not os.path.isdir(f"{self._outdir}/z_max_projection"):
                os.makedirs(f"{self._outdir}/z_max_projection", mode=0o755)
            for channel in ["blue", "green", "yellow", "red"]:
                if not os.path.isdir(f"{self._outdir}/z_max_projection/{channel}"):
                    os.makedirs(f"{self._outdir}/z_max_projection/{channel}", mode=0o755)
                data_dir = f"{self._outdir}/deconvoluted_images/{channel}"
                self.z_projection(data_dir, f"{self._outdir}/z_max_projection/{channel}", dz=1, dx=1)
                all_items = os.listdir(f"{self._outdir}/z_max_projection/{channel}")
                print(f"{self._outdir}/z_max_projection/{channel}: {len(all_items)}")
            # ### Image embedding
            self.generate_node_attribute(f"{self._outdir}/z_max_projection", f"{self._outdir}/z_max_projection")
            if not os.path.isdir(f"{self._outdir}/embedding"):
                os.makedirs(f"{self._outdir}/embedding", mode=0o755)

            self.cellmaps_image_embedding(
                f"{self._outdir}/z_max_projection",
                self.provenance_img,
                f"{self._outdir}/embedding/img_embedding",
            )
            ### Handle multiple images problem
            img_emb = pd.read_csv(f"{self._outdir}/embedding/img_embedding/image_emd.tsv",
                              sep = '\t', index_col = 0).groupby(level=0).mean()
            img_emb.to_csv(f"{self._outdir}/embedding/img_embedding/image_emd.tsv", 
                           sep = '\t', header= False)
            self.cellmaps_PPI_embedding(
                self.ppi_dir,
                self.provenance_ppi,
                f"{self._outdir}/embedding/ppi_embedding",
            )
            self.cellmaps_co_embedding(
                f"{self._outdir}/embedding/img_embedding",
                f"{self._outdir}/embedding/ppi_embedding",
                f"{self._outdir}/embedding/co_embedding",
                self.k
            )
            if self.generate_hierarchy:
                self.cellmaps_generate_hierarchy(
                    f"{self._outdir}/embedding/co_embedding", f"{self._outdir}/embedding/hierarchy"
                )
                self.cellmaps_hierarchyeval(
                    f"{self._outdir}/embedding/hierarchy", f"{self._outdir}/embedding/hierarchy_eval"
                )

            # set exit code to value passed in via constructor
            exitcode = self._exitcode
        finally:
            # write a task finish file
            logutils.write_task_finish_json(outdir=self._outdir, start_time=self._start_time, status=exitcode)

        return exitcode
