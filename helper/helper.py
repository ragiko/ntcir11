#!/usr/bin/python
# -*- coding: utf-8 -*-


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


