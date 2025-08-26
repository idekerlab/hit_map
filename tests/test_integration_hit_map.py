#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Integration Tests for `hit_map` package."""

import os

import unittest
from hit_map import hit_mapcmd

SKIP_REASON = 'HIT_MAP_INTEGRATION_TEST ' \
              'environment variable not set, cannot run integration ' \
              'tests'

@unittest.skipUnless(os.getenv('HIT_MAP_INTEGRATION_TEST') is not None, SKIP_REASON)
class TestIntegrationHit_map(unittest.TestCase):
    """Tests for `hit_map` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_something(self):
        """Tests parse arguments"""
        self.assertEqual(1, 1)
