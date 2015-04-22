#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import hymlab.text as ht

def output_result(res, result_path):
    """
    クエリとドキュメントの類似度の結果を保存
    [[(text, sim), (text, sim), ...],
    [(text, sim), (text, sim), ...],
    [(text, sim), (text, sim), ...],...]
    """
    # fileのアウトプット
    for i in range(len(res)):
        query_res = res[i]
        query_res = sorted(query_res, key=lambda x: x[1], reverse=True)[0:1000]

        f = open(result_path + "/" + str(i+1).zfill(2) + ".txt", "w")
        s = ""
        for doc_id, (doc_text, sim) in enumerate(query_res):
            s += doc_text.path + " " + str(sim) + "\n"

        f.write(s)
        f.close()

def similarity_output_result(results, result_path):
    """
    Similarityクラスのインスタンスを結果として吐き出す
    """
    res = []
    for query_result in results:
        # TODO: text2.textのところ修正必要
        t = [(text2.text, sim) for text1, text2, sim in query_result]
        res.append(t)
    output_result(res, result_path)

def doc_text_cache_load(doc_path, output_path):
    """
    検索文書のテキストを取得する
    キャッシュロード
    :param doc_path:
    :param output_path:
    :return:
    """
    if (os.path.exists(output_path) == False):
        doc_tc = ht.TextCollection(doc_path)
        ht.pickle_save(doc_tc, output_path)
    else:
        doc_tc = ht.pickle_load(output_path)
    return doc_tc

def doc_tf_cache_load(doc_path, output_path, normarize=True):
    """
    検索文書のtf取得する
    キャッシュロード
    :param doc_path:
    :param output_path: 
    :return:
    """
    # ドキュメントを読み込み
    if (os.path.exists(output_path) == False):
        doc_tc = ht.TextCollection(doc_path)
        doc_tf = ht.TfIdf(doc_tc).tf(normarize)
        ht.pickle_save(doc_tf, output_path)
    else:
        doc_tf = ht.pickle_load(output_path)
    return doc_tf

def doc_idf_cache_load(doc_path, output_path):
    """
    検索文書のtf取得する
    キャッシュロード
    :param doc_path:
    :param output_path:
    :return:
    """
    # ドキュメントを読み込み
    if (os.path.exists(output_path) == False):
        doc_tc = ht.TextCollection(doc_path)
        doc_idf = ht.TfIdf(doc_tc).idf()
        ht.pickle_save(doc_idf, output_path)
    else:
        doc_idf = ht.pickle_load(output_path)
    return doc_idf


def query_tf_cache_load(query_path, output_path, normalize=True):
    """
    クエリ文書のtfを取得する
    キャッシュロード
    :param query_path: 
    :param output_path: 
    :return:
    """
    if (os.path.exists(output_path) == False):
        query = ht.file_read(query_path).split("\n")
        query.pop()
        q_tc = ht.TextCollection(query)
        # 正規化TFではないので注意
        q_tf_list = ht.TfIdf(q_tc).tf(normalize)
        ht.pickle_save(q_tf_list, output_path)
    else:
        q_tf_list = ht.pickle_load(output_path)
    return q_tf_list
