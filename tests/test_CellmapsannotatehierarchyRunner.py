#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cellmaps_annotate_hierarchy` package."""


import unittest
from cellmaps_annotate_hierarchy.runner import CellmapsannotatehierarchyRunner


class TestCellmapsannotatehierarchyrunner(unittest.TestCase):
    """Tests for `cellmaps_annotate_hierarchy` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_constructor(self):
        """Tests constructor"""
        myobj = CellmapsannotatehierarchyRunner(0)

        self.assertIsNotNone(myobj)

    def test_run(self):
        """ Tests run()"""
        myobj = CellmapsannotatehierarchyRunner(4)
        self.assertEqual(4, myobj.run())
