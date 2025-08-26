#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `hit_map` package."""

import os
import tempfile
import shutil


import unittest
from hit_map import hit_mapcmd


class TestHit_map(unittest.TestCase):
    """Tests for `hit_map` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_parse_arguments(self):
        """Tests parse arguments"""
        res = hit_mapcmd._parse_arguments('hi', ['dir'])

        self.assertEqual('dir', res.outdir)
        self.assertEqual(1, res.verbose)
        self.assertEqual(0, res.exitcode)
        self.assertEqual(None, res.logconf)

        someargs = ['dir', '-vv', '--logconf', 'hi', '--exitcode', '3']
        res = hit_mapcmd._parse_arguments('hi', someargs)

        self.assertEqual('dir', res.outdir)
        self.assertEqual(3, res.verbose)
        self.assertEqual('hi', res.logconf)
        self.assertEqual(3, res.exitcode)


    def test_main(self):
        """Tests main function"""

        temp_dir = tempfile.mkdtemp()
        # try where loading config is successful
        try:
            outdir = os.path.join(temp_dir, 'out')
            res = hit_mapcmd.main(['myprog.py', outdir, '--skip_logging'])
            self.assertEqual(res, 0)
        finally:
            shutil.rmtree(temp_dir)
