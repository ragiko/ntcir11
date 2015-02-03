#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import hymlab.text as ht

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../helper')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../config')
import helper
import config

import unittest

from collections import defaultdict

class PmiModel:
    def __init__(self):
        self.PMI_PATH = conf.PROJECT_PATH + "/data/csjPMI_normalized.txt"
        self.pmi_dict = self.pmi_init() 

    def pmi_init(self):
        pmi_list = ht.file_read(self.PMI_PATH).split("\n")
        pmi_list.pop()

        pmi_dict = defaultdict(dict)
        for pmi in pmi_list:
            pmi_element = pmi.split("\t")
            word1 = pmi_element[0]
            word2 = pmi_element[1]
            value = float(pmi_element[2])

            pmi_dict[word1][word2] = value # init
        return pmi_dict

    def sum_pmi_vector(self, words):
        """
        文書の単語群からsum pmiベクトルを返却
        return: dist
        """
        res = {}
        for word in words:
            res[word] = self.sum_pmi(word, words)
        return res

    def sum_pmi(self, term, text):
        """
        文書と単語からsum pmiを計算する
        @param: term "w1"
        @param: text ["w1", "w2", ...]
        """
        score = 0.0
        for word in text:
            score += self.get(term, word) 
        return score

    # w1 w2 と w2 w1 のときも同じ計算を出さないとだめ
    def get(self, word1, word2):
        """
        単語を２通りの順序調べて、値があるものを返却する
        """
        try:
            v1 = self.pmi_dict[word1][word2]
        except:
            v1 = 0.0 
        try:
            v2 = self.pmi_dict[word2][word1]
        except:
            v2 = 0.0 
    
        if v1 == 0.0 and v2 == 0.0:
            return 0.0
        elif v1 == 0.0:
            return v2
        elif v2 == 0.0:
            return v1
    
        else:
            return 0.0

if __name__ == '__main__':
    """
    main program
    """
    # データの設定
    conf = config.Config("pmi")
    QUERY_PATH = conf.SPOKEN_QUERY_PATH
    DOC_PATH = conf.SPOKEN_DOC_PATH

    pmi_model = PmiModel()
    # ht.pp(pmi_model.get(u"鼻声", u"音声")) # test:

    # クエリを取得してきて一文書に対してsum pmiベクトルを計算
    # クエリを読み込み
    QUERY_PATH = conf.WRITE_QUERY_PATH
    query = ht.file_read(QUERY_PATH).split("\n")
    query.pop()
    query_tc = ht.TextCollection(query)
    ht.pp(pmi_model.sum_pmi_vector(query_tc[0].words()))

    # pmi ベクトル
    # 入力 term, text 結果 sum pmiの値



    # DOC_PATH = conf.WRITE_DOC_PATH



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

