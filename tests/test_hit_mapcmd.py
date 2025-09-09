#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `hit_map` package."""

import os
import tempfile
import shutil
import unittest
from unittest.mock import patch
import numpy as np

from hit_map import hit_mapcmd


class TestHit_map(unittest.TestCase):
    """Tests for `hit_map` package."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_arguments(self):
        """Tests parse arguments"""
        # use --outdir (option) instead of positional
        res = hit_mapcmd._parse_arguments('hi', ['--outdir', 'dir'])

        self.assertEqual('dir', res.outdir)
        self.assertEqual(1, res.verbose)
        self.assertEqual(0, res.exitcode)
        self.assertEqual(None, res.logconf)

        someargs = ['--outdir', 'dir', '-vv', '--logconf', 'hi', '--exitcode', '3']
        res = hit_mapcmd._parse_arguments('hi', someargs)

        self.assertEqual('dir', res.outdir)
        self.assertEqual(3, res.verbose)
        self.assertEqual('hi', res.logconf)
        self.assertEqual(3, res.exitcode)

    def test_main(self):
        """Tests main function"""
        temp_dir = tempfile.mkdtemp()
        try:
            outdir = os.path.join(temp_dir, 'out')

            # create a minimal .npy for microscope_setup_param expected by the runner
            ms_params_path = os.path.join(temp_dir, 'microscope.npy')
            # keep keys generic; runner only needs to be constructible for this test
            np.save(ms_params_path, {'ni': 1.33,
                'NA': 1.4,
                'resxy': 65,
                'resz': 250,
                'threads': 1,
                'lamb da': []  # keep empty so the loop would be trivial if run
            })

            # Mock HitmapRunner.run so main returns 0 without executing pipeline
            with patch('hit_map.hit_mapcmd.HitmapRunner.run', return_value=0):
                res = hit_mapcmd.main([
                    'hit_mapcmd.py',
                    '--outdir', outdir,
                    '--microscope_setup_param', ms_params_path,
                    '--skip_logging'
                ])
                self.assertEqual(res, 0)
        finally:
            shutil.rmtree(temp_dir)
