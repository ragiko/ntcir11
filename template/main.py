#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import hymlab.text as ht

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../helper')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../config')
import helper
import config

import unittest

if __name__ == '__main__':
    """
    main program
    """
    # データの設定
    conf = config.Config("bm25")
    QUERY_PATH = conf.SPOKEN_QUERY_PATH
    DOC_PATH = conf.SPOKEN_DOC_PATH

    pass

    """
    test case
    """
    # class ATestCase(unittest.TestCase):
    #     def setUp(self):
    #         pass
    #    
    #     def tearDown(self):
    #         pass
    #
    #     def test_a(self):
    #         pass
    # unittest.main()

