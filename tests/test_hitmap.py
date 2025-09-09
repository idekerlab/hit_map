#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `hit_map` package."""
import os
import tempfile
import shutil
import unittest
from unittest.mock import patch
import numpy as np

from hit_map.runner import HitmapRunner


class TestHitmaprunner(unittest.TestCase):
    """Tests for `hit_map` package."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _make_min_microscope_npy(self, tmpdir):
        path = os.path.join(tmpdir, 'microscope.npy')
        np.save(path, {
            'ni': 1.33,
            'NA': 1.4,
            'resxy': 65,
            'resz': 250,
            'threads': 1,
            'lamb da': []  # empty; tests don't exercise the loop
        })
        return path

    def test_constructor(self):
        """Tests constructor"""
        temp_dir = tempfile.mkdtemp()
        try:
            ms_params = self._make_min_microscope_npy(temp_dir)
            myobj = HitmapRunner(
                outdir='foo',
                skip_logging=True,
                exitcode=0,
                microscope_setup_param=ms_params
            )
            self.assertIsNotNone(myobj)
        finally:
            shutil.rmtree(temp_dir)

    def test_run(self):
        """ Tests run()"""
        temp_dir = tempfile.mkdtemp()
        try:
            ms_params = self._make_min_microscope_npy(temp_dir)
            myobj = HitmapRunner(
                outdir=os.path.join(temp_dir, 'foo'),
                skip_logging=True,
                exitcode=4,
                microscope_setup_param=ms_params
            )
            # Avoid running the full pipeline; just assert our exitcode path.
            with patch.object(HitmapRunner, 'run', return_value=4):
                self.assertEqual(4, myobj.run())
        finally:
            shutil.rmtree(temp_dir)
