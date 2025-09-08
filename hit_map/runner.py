#! /usr/bin/env python

import os
import time
import logging
from cellmaps_utils import logutils
from cellmaps_utils.provenance import ProvenanceUtil
from hit_map.exceptions import HitmapError
import cv2
import numpy as np
import shutil
import pandas as pd
import multipagetiff as mtif
from matplotlib import pyplot as plt
import re
import json
import sys
from scipy import stats
import hit_map

logger = logging.getLogger(__name__)


class HitmapRunner(object):
    """
    Class to run algorithm
    """
    def __init__(self, 
                 image_meta = None,
                 ppi_dir = None,
                 microscope_setup_param = None,
                 psigma =None,
                 outdir=None,
                 provenance_img = None,
                 provenance_ppi = None,
                 generate_hierarchy = True,
                 exitcode=None,
                 skip_logging=True,
                 input_data_dict=None,
                 provenance_utils=ProvenanceUtil()):
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
            raise HitmapError('outdir is None')
        self.image_meta =image_meta
        self.ppi_dir = ppi_dir
        self.microscope_setup_param = microscope_setup_param
        self.psigma =psigma
        self.provenance_img = provenance_img
        self.provenance_ppi = provenance_ppi
        self.provenance_ppi = provenance_ppi
        self.generate_hierarchy = generate_hierarchy
        
        self._outdir = os.path.abspath(outdir)

        
        self._exitcode = exitcode
        self._start_time = int(time.time())
        if skip_logging is None:
            self._skip_logging = False
        else:
            self._skip_logging = skip_logging
        self._input_data_dict = input_data_dict
        self._provenance_utils = provenance_utils

        logger.debug('In constructor')
    
    ### Image deconvolution functions 
    def generate_theoretical_PSF(ni,NA,lamb,resxy, resz, save_dir, threads=4):
        ### Need to install deconwolf/0.4.2
         """
            :param ni: refractive index
            :param NA: numerical aperture
            :param lamb: wavelength 
            :param resxy: pixel size
            :param resz: destance between panels 
            :save_dir: output file with name and directory
            :param threads: integer, for multiprocessing
            """
            subprocess.run(["dw_bw",f"--ni {ni}",
                           f"--NA {NA}", f"--lambda {lamb}",
                           f"--resxy {resxy}", f"--resz {resz}",
                            f"--threads {threads}", save_dir])
    def format_deconwolf(image_dir, psf_dir,psigma,save_prefix,iteration = 100):
        subprocess.run("dw", f"--iter {iteration}",
                       image_dir, psf_dir, f"--psigma {psigma}", 
                       f"--prefix {save_prefix}" )
        
    def z_max_projection(img_stack,channel= 0):
        #channel 0 is defualt channel to stack 
        return np.max(img_stack,axis=channel)
    def enhance_contrast(img,saturation_level=0.7):
        clahe = cv2.createCLAHE(clipLimit = saturation_level, tileGridSize=(8,8))
        enhanced_L = clahe.apply(img)
        return enhanced_L
    
    def z_projection(image_dir,save_dir, dz=1,dx=1):
        for image in os.listdir(image_dir):
            if image.endswith('.tif'):
                stack = mtif.read_stack(f'{image_dir}/{image}', dx=1, dz=1, units='nm')
                stack = stack.pages
                z_max = z_max_projection(stack)
                image_8bit = cv2.normalize(z_max, None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
                z_max = enhance_contrast(image_8bit)
                save_name = '_'.join(image.split('_'))[:-4] +  '_'+f'{color}'+'.jpg'
                cv2.imwrite(f'{save_dir}/{save_name}', z_max) 
            else:
                suffix = image_dir.split('.')[-1]
                raise TypeError(f"Expect .tif images, but got .{suffix}")
    def generate_node_attribute(input_dir,save_dir):
        filename =[]
        name =[]
        for file in os.listdir(f'{input_dir}/blue'):
            if file.endswith('.jpg'):
                filename.append('_'.join(file.split('_')[:-1])+'_')
                name.append(file.split('_')[0])
        df = pd.DataFrame({'name':name,'filename':filename})
        df.to_csv(f'{save_dir}/1_image_gene_node_attributes.tsv',sep='\t', index=False)
    
    def cellmaps_image_embedding(image_dir,provenance,outdir):
        subprocess.run("cellmaps_image_embeddingcmd.py", outdir,
                       f"--inputdir {image_dir}", f"--provenance {provenance}")
    def cellmaps_PPI_embedding(ppi_score_file,provenance,outdir):
        subprocess.run("cellmaps_ppi_embeddingcmd.py", outdir,
                       f"--inputdir {image_dir}", f"--provenance {provenance}")
    def cellmaps_co_embedding(image_embedding_dir, ppi_embedding_dir,outdir):
        subprocess.run("cellmaps_coembeddingcmd.py", outdir,
                       f"--embeddings {image_embedding_dir} {ppi_embedding_dir}")
    def cellmaps_generate_hierarchy(co_embedding_dir, out_dir):
        subprocess.run(f"cellmaps_generate_hierarchycmd.py", out_dir, f"--coembedding_dirs {co_embedding_dir}") 
    def cellmaps_hierarchyeval(hierarchy_dir, outdir):
        subprocess.run("cellmaps_hierarchyevalcmd.py", outdir, f"--hierarchy_dir {hierarchy_dir}")
    
    def run(self):
        """
        Runs HIT-MAP


        :return:
        """
        'image meta file with the following columns'
                       'file_directory: image direcotry'
                       'channel: blue: nucleus, green: targeted protein,red: microtubule yellow:ER'
                       'targetted_proteins: targetting protein of interest '
                       'save_prefix: save file prefix'
        if not os.path.isdir(self._outdir):
                os.makedirs(self._outdir, mode=0o755)
        ### Generate the psf files
        for key,value in self.microscope_setup_param['lambda']:
            if not os.path.isdir(f'{self._outdir}/theoretical_psf'):
                os.makedirs(f'{self._outdir}/theoretical_psf', mode=0o755)

                
            generate_theoretical_PSF(self.microscope_setup_param['ni'],
                                     self.microscope_setup_param['NA'],
                                     value,self.microscope_setup_param['resxy'],
                                     self.microscope_setup_param['resz'],
                                     f'{self._outdir}/theoretical_psf/{key}_psf.tiff', 
                                     threads = self.microscope_setup_param['threads'])
        print('Successfully generated theoretical PSF.')
        
        ### Image deconvolution 
        image_meta = pd.read_csv(self.image_meta,sep = '\t')
        if not os.path.isdir(f'{self._outdir}/deconvoluted_images'):
            os.makedirs(f'{self._outdir}/deconvoluted_images', mode=0o755)
        if not os.path.isdir(f'{self._outdir}/deconvoluted_images/blue'):
            os.makedirs(f'{self._outdir}/deconvoluted_images/blue', mode=0o755)
        if not os.path.isdir(f'{self._outdir}/deconvoluted_images/red'):
            os.makedirs(f'{self._outdir}/deconvoluted_images/red', mode=0o755)
        if not os.path.isdir(f'{self._outdir}/deconvoluted_images/green'):
            os.makedirs(f'{self._outdir}/deconvoluted_images/green', mode=0o755)
        if not os.path.isdir(f'{self._outdir}/deconvoluted_images/yellow'):
            os.makedirs(f'{self._outdir}/deconvoluted_images/yellow', mode=0o755)
        if not os.path.isdir(f'{self._outdir}/deconvoluted_logs'):
            os.makedirs(f'{self._outdir}/deconvoluted_logs', mode=0o755)
        for i in image_meta.index.values:
            format_deconwolf(image_meta.at[i,'file_directory'],
                              f'{self._outdir}/theoretical_psf/{image_meta.at[i,'channel']}_psf.tiff',
                              self.psigma,
                              image_meta.at[i,'save_prefix'],
                              iteration = 100)
            src = f'./{image_meta.at[i,'save_prefix']}_{file_directory.split('/')[-1]}'
            dst =  f'{self._outdir}/deconvoluted_images/{image_meta.at[i,'channel']}/{image_meta.at[i,'save_prefix']}_{file_directory.split('/')[-1]}'
            ### Move the deconvoluted files
            shutil.move(src, dst)
            shutil.move(f"{src}.log.txt", f'{self._outdir}/deconvoluted_logs/{image_meta.at[i,'channel']}_{image_meta.at[i,'save_prefix']}_{file_directory.split('/')[-1]}.log.txt')
        ### check the deconvolution output
        all_items = os.listdir(f'{self._outdir}/deconvoluted_images/yellow')
        print(f'{self._outdir}/deconvoluted_images/yellow: {len(all_items)}')
        all_items = os.listdir(f'{self._outdir}/deconvoluted_images/green')
        print(f'{self._outdir}/deconvoluted_images/green: {len(all_items)}')
        all_items = os.listdir(f'{self._outdir}/deconvoluted_images/red')
        print(f'{self._outdir}/deconvoluted_images/red: {len(all_items)}')
        all_items = os.listdir(f'{self._outdir}/deconvoluted_images/blue')
        print(f'{self._outdir}/deconvoluted_images/blue: {len(all_items)}')
        
        ### Deconvolution images z_max projection and enhancing 
        if not os.path.isdir(f'{self._outdir}/z_max_projection'):
            os.makedirs(f'{self._outdir}/z_max_projection', mode=0o755)
        for channel in ['blue','green','yellow','red']:
             if not os.path.isdir(f'{self._outdir}/z_max_projection/{channel}'):
                os.makedirs(f'{self._outdir}/z_max_projection/{channel}', mode=0o755)
            data_dir = f'{self._outdir}/deconvoluted_images/{channel}'
            z_projection(data_dir,f'{self._outdir}/z_max_projection/{channel}', dz=1,dx=1)
            all_items = os.listdir(f'{self._outdir}/z_max_projection/{channel}')
            print(f'{self._outdir}/z_max_projection/{channel}: {len(all_items)}')
        ### Image embedding 
        generate_node_attribute(f'{self._outdir}/z_max_projection',f'{self._outdir}/z_max_projection')
        if not os.path.isdir(f'{self._outdir}/embedding'):
            os.makedirs(f'{self._outdir}/embedding', mode=0o755)
       
        cellmaps_image_embedding(f'{self._outdir}/z_max_projection',self.provenance_img,f'{self._outdir}/embedding/img_embedding')
        cellmaps_image_embedding(self.ppi_dir,self.provenance_ppi,f'{self._outdir}/embedding/ppi_embedding')
        cellmaps_co_embedding(f'{self._outdir}/embedding/img_embedding', f'{self._outdir}/embedding/ppi_embedding',f'{self._outdir}/embedding/co_embedding')
        if self.generate_hierarchy:
            cellmaps_generate_hierarchy(f'{self._outdir}/embedding/co_embedding', f'{self._outdir}/embedding/hierarchy')
            cellmaps_hierarchyeval(f'{self._outdir}/embedding/hierarchy', f'{self._outdir}/embedding/hierarchy_eval'):
          
        exitcode = 99
        try:
            logger.debug('In run method')
            if os.path.isdir(self._outdir):
                raise HitmapError(self._outdir + ' already exists')
            if not os.path.isdir(self._outdir):
                os.makedirs(self._outdir, mode=0o755)
            if self._skip_logging is False:
                logutils.setup_filelogger(outdir=self._outdir,
                                          handlerprefix='hit_map')
            logutils.write_task_start_json(outdir=self._outdir,
                                           start_time=self._start_time,
                                           data={'commandlineargs': self._input_data_dict},
                                           version=hit_map.__version__)

            # set exit code to value passed in via constructor
            exitcode = self._exitcode
        finally:
            # write a task finish file
            logutils.write_task_finish_json(outdir=self._outdir,
                                            start_time=self._start_time,
                                            status=exitcode)


        return exitcode
