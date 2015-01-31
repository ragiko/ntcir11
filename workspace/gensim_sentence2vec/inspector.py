#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, codecs
import re 

import hymlab.text as ht
from main import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../helper')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../config')
import helper
import config

if __name__ == '__main__':
    corpus = Corpus()
    print "make corpus"
    corpus.all_tc.info()
 
