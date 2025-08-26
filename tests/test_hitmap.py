#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `hit_map` package."""
import os
import tempfile
import shutil

import unittest
from hit_map.runner import HitmapRunner


class TestHitmaprunner(unittest.TestCase):
    """Tests for `hit_map` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_constructor(self):
        """Tests constructor"""
        myobj = HitmapRunner(outdir='foo', skip_logging=True,
                                                       exitcode=0)

        self.assertIsNotNone(myobj)

    def test_run(self):
        """ Tests run()"""
        temp_dir = tempfile.mkdtemp()
        try:
            myobj = HitmapRunner(outdir=os.path.join(temp_dir, 'foo'),
                                                         skip_logging=True,
                                                         exitcode=4)
            self.assertEqual(4, myobj.run())
        finally:
            shutil.rmtree(temp_dir)
