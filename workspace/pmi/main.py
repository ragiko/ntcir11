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

def merge_vector(tfidf_vec, sumpmi_vec):
    """
    tfidfとsumpmiの結合
    sumpmiの値が0以下の時、tfidfの値を0に更新
    """
    res = {}
    if len(tfidf_vec.keys()) != len(sumpmi_vec.keys()): 
        raise NameError('dict size is not match')

    for word, sum_v in sumpmi_vec.items(): 
        if sum_v < 0.0:
            res[word] = 0.0
        else:
            res[word] = tfidf_vec[word]
    return res

def merge_tfidf_pmi_features(tfidf_features, pmi_model, use_merge=True):
    """
    sumpmiで補正したtfidfのベクトルを作成
    @param: tfidf_features 自分のモジュールのtfidfの値
    @param: pmi_model 自分のpmiクラスのインスタンス
    """
    # query tfidf (sumpmi補正)
    tfidf_pmi = []
    for tfidf in tfidf_features:
        tfidf_vec = tfidf.vec
        sumpmi_vec = pmi_model.sum_pmi_vector(tfidf.text.words())
        if use_merge:
            merge_vec = merge_vector(tfidf_vec, sumpmi_vec)
        else: 
            merge_vec = tfidf_vec
        tfidf_pmi.append((tfidf.text, merge_vec)) 
    return tfidf_pmi

if __name__ == '__main__':
    """
    main program
    """
    # データの設定
    conf = config.Config("pmi")
    QUERY_PATH = conf.SPOKEN_QUERY_PATH
    DOC_PATH = conf.SPOKEN_DOC_PATH
    conf.RESULT_PATH

    pmi_model = PmiModel()
    # ht.pp(pmi_model.get(u"鼻声", u"音声")) # test:

    # クエリを取得してきて一文書に対してsum pmiベクトルを計算
    # クエリを読み込み
    query = ht.file_read(QUERY_PATH).split("\n")
    query.pop()
    query_tc = ht.TextCollection(query)
    query_tfidf_features = ht.TfIdf(query_tc).tf_idf()
    query_tfidf_pmi = merge_tfidf_pmi_features(query_tfidf_features, pmi_model, use_merge=False)

    # ドキュメントを読み込み
    doc_tc = ht.TextCollection(DOC_PATH)

    # cache
    DOC_TF_IDF_PATH = conf.TMP_PATH + "/doc_tfidf"
    doc_tfidf_features = None
    if (os.path.exists(DOC_TF_IDF_PATH) == False):
        doc_tfidf_features = ht.TfIdf(doc_tc).tf_idf()
        ht.pickle_save(doc_tfidf_features, DOC_TF_IDF_PATH)
    else:
        doc_tfidf_features = ht.pickle_load(DOC_TF_IDF_PATH)
    doc_tfidf_pmi = merge_tfidf_pmi_features(doc_tfidf_features, pmi_model, use_merge=False)

    # 類似度計算
    res = []
    doc_sim = ht.Similarity(doc_tfidf_pmi)
    for q_feature in query_tfidf_pmi:
        res.append(doc_sim.most_similarity_by_feature(q_feature))

    # 結果の出力
    helper.similarity_output_result(res, conf.RESULT_PATH)

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

