#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import hymlab.text as ht

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../helper')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../config')
import helper
import config

import unittest
from math import log

if __name__ == '__main__':
    """
    main program

    * コーパス変更
    * 対数尤度について
    * ワードがコーパスにもない場合
    * クエリ尤度は関数化して外に出すべき
    """
    # データの設定
    conf = config.Config("query_likelihood")

    QUERY_PATH = conf.WRITE_QUERY_PATH
    DOC_PATH = conf.WRITE_DOC_PATH

    # csjに要変更
    DOC_CORPUS_PATH = conf.WRITE_DOC_PATH 

    # クエリを読み込み
    query = ht.file_read(QUERY_PATH).split("\n")
    query.pop()
    q_tc = ht.TextCollection(query)

    # ドキュメントを読み込み
    doc_tc = ht.TextCollection(DOC_PATH)
    # tf
    doc_tf = ht.TfIdf(doc_tc).tf()

    #  コーパスのtf
    # doc_tc = ht.TextCollection(DOC_CORPUS_PATH)
    texts_str = doc_tc.merge_texts()
    corpus_doc_tc = ht.TextCollection([texts_str])
    corpus_doc_tf = ht.TfIdf(corpus_doc_tc).tf()

    # params
    tf_corpus = corpus_doc_tf[0].vec
    omega = 0.4
    init_not_word = 0.0000001

    result = []
    # query loop
    for query_text in q_tc.list(): 
        query_result = []

        # doc loop
        for doc_tf_vsm in doc_tf:
            tf = doc_tf_vsm.vec 
            likelifood = 0.0

            # query word loop
            for word in query_text.words():
                likelifood += log(omega*tf.get(word, init_not_word) + (1-omega)*tf_corpus.get(word, init_not_word))

            query_result.append((doc_tf_vsm.text, likelifood))

        result.append(query_result)

    # 結果を出力
    print conf.RESULT_PATH
    helper.output_result(result, conf.RESULT_PATH)

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

