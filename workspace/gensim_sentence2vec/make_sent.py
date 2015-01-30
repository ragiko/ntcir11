#!/usr/bin/python
# -*- coding: utf-8 -*-

import hymlab.text as ht
from gensim.models.doc2vec import *

if __name__ == '__main__':
    WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
    QUERY_FILE_PATH = WORKSPACE_DIR + "/../../NTCIR11/Data/formalrun_query/formalrun_query.txt" # 認識結果
    DOC_DIR_PATH = WORKSPACE_DIR + "/../../NTCIR11/Data/slide_asr_noblank" # 認識結果
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

    # コーパス作成
    merge_tc.dump_corpus(TMP_DIR_PATH+"/corpus.txt")

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
