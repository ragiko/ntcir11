#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

# TODO: パッケージのインポートの書き方を勉強
from hymlab.text.util import *
from hymlab.text.vital import *
from hymlab.text.text import *
from hymlab.text.similarity import *
from hymlab.text.feature.feature import *
from hymlab.text.feature.tfidf import *

if __name__ == '__main__':
    WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

    QUERY_FILE_PATH = WORKSPACE_DIR + "/../NTCIR11/Data/formalrun_query/formalrun_query_text.txt"
    DOC_DIR_PATH = WORKSPACE_DIR + "/../NTCIR11/Data/slide_asr_noblank"

    QUERY_TFIDF_PATH = WORKSPACE_DIR + "/tmp/query_tfidf"
    DOC_TFIDF_PATH = WORKSPACE_DIR + "/tmp/doc_tfidf"

    RESULT_DIR_PATH = WORKSPACE_DIR + "/result"

    # クエリに対して素性を取得
    query_tfidf = None
    if (os.path.exists(QUERY_TFIDF_PATH) == False):
        query = file_read(QUERY_FILE_PATH).split("\n")
        query = query[0:(len(query)-1)]
        q_tc = TextCollection(query)
        q_tfidf = TfIdf(q_tc).run()
        # キャッシュ
        pickle_save(q_tfidf, QUERY_TFIDF_PATH)
        query_tfidf = q_tfidf
    else:
        query_tfidf = pickle_load(QUERY_TFIDF_PATH)

    # 検索文書に対して素性を取得
    doc_tfidf = None
    if (os.path.exists(DOC_TFIDF_PATH) == False):
        d_tc = TextCollection(DOC_DIR_PATH)
        d_tfidf = TfIdf(d_tc).run()
        # キャッシュ
        pickle_save(d_tfidf, DOC_TFIDF_PATH)
        doc_tfidf = d_tfidf
    else:
        doc_tfidf = pickle_load(DOC_TFIDF_PATH)

    # 類似度計算
    doc_sim_extractor = Similarity(doc_tfidf)
    for i, q_feature in enumerate(query_tfidf):
        sim = doc_sim_extractor.most_similarity_future_by_outer_feature(q_feature)

        # 結果を出力
        f = open(RESULT_DIR_PATH + "/" + str(i+1).zfill(2) + ".txt", "w")
        for s in sim:
            f.write(s.vsm2.text.path + " " + str(s.similarity) + "\n")
        f.close()
        pp(len(sim))
