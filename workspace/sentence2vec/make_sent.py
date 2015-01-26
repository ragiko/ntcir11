#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
import hymlab.text as ht
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/sentence2vec_core')
from word2vec import Word2Vec, Sent2Vec, LineSentence

if __name__ == '__main__':
    """
    10次元で2.08sかかる
    """
    logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
    logging.info("running %s" % " ".join(sys.argv))

    WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
    QUERY_FILE_PATH = WORKSPACE_DIR + "/../../NTCIR11/Data/formalrun_query/formalrun_query.txt" # 認識結果
    DOC_DIR_PATH = WORKSPACE_DIR + "/../../NTCIR11/Data/slide_asr_noblank" # 認識結果
    RESULT_DIR_PATH = WORKSPACE_DIR + "/result"
    TMP_DIR_PATH = WORKSPACE_DIR + "/middle" 

    # クエリを読み込み
    query = ht.file_read(QUERY_FILE_PATH).split("\n")
    query = query[0:(len(query)-1)]
    q_tc = ht.TextCollection(query)

    # ドキュメントを読み込み
    d_tc = ht.TextCollection(DOC_DIR_PATH)

    # クエリとドキュメントのマージ
    q_tc.add_text_collection(d_tc)
    merge_tc = q_tc

    # 文章の絶対位置のインデックスを作成
    f = open(TMP_DIR_PATH + "/file_index.txt", "w")
    s = ""
    for text in merge_tc.list():
        if text.path is None:
            s = "query\n"
        else:
            s = text.path+"\n"
        f.write(s)
    f.close()

    # コーパス作成
    merge_tc.dump_corpus(TMP_DIR_PATH+"/corpus.txt")

    # word2vec
    input_file = 'corpus.txt'
    model = Word2Vec(LineSentence(TMP_DIR_PATH + "/" + input_file), size=10, window=5, sg=0, min_count=5, workers=8)
    model.save(TMP_DIR_PATH + "/" + input_file + '.model')
    model.save_word2vec_format(TMP_DIR_PATH + "/" + input_file + '.vec')

    # pragraph2vec 
    sent_file = 'sent.txt'
    model = Sent2Vec(LineSentence(TMP_DIR_PATH+"/"+sent_file), model_file=TMP_DIR_PATH+"/"+input_file+'.model')
    model.save_sent2vec_format(TMP_DIR_PATH+"/"+sent_file+'.vec')

