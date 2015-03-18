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
import re

def web_str_normalize(str):
    '''
    webのコンテンツの不必要な文字を削除
    
    TODO: ロシア語とかノイズで残る
    :param str:
    :return:
    '''
    # 改行の削除
    s = str.replace("\n", '')
    # 半角の連続を削除 (英文, プログラム)
    s = re.sub(r'[!-~A-Z ]{15,}', '', s)
    # 記号の連続を削除 (顔文字, その他)
    s = re.sub(r'[ﾉ|ノ|v|U|o|O|q|p|T|x|X|ｰ|ﾟ|｡|、|。|，|．|･|・|：|；|？|！|゛|゜|｀|´|¨|＾|>丶|＿|￣|ヽ|ヾ|ゝ|ゞ|〃|仝|々|〆|〇|ー|―|‐|／|＼|～|∥|｜|…|‥|‘|’|“|”|（|）|〔|〕|［|］|｛|｝|〈|〉|《|》|「|」|『|』|【|】|＋|－|±|×|÷|＝|≠|＜|＞|≦|≧|∞|∴|♂|♀|°|′|″|℃|￥|＄|￠|￡|％|＃|>＆|＊|＠|§|☆|★|○|●|◎|◇|◆|□|■|△|▲|▽|▼|※|〒|→|←|↑|↓|〓|∈|∋|⊆|⊇|⊂|⊃|∪|∩|∧|∨|￢|⇒|⇔|∀|∃|∠|⊥|⌒|∂|∇|≡|≒|≪|≫|√|∽|∝|∵|∫|∬|Å|‰|♯|♭|♪|†|‡|¶|Γ|Δ|Θ|Λ|Ξ|Π|Σ|>Φ|Χ|Ψ|Ω|α|β|γ|δ|ε|ζ|η|θ|ι|κ|λ|μ|ν|ξ|ο|π|ρ|σ|τ|υ|φ|χ|ψ|ω|Б|Г|Д|Ё|Ж|З|И|Й|К|Л|П|Ф|Ц|Ч|Ш|Щ|Ъ|Ы|Э|Ю|Я|б|в|г|д|е|ё|ж|з|и|й|к|л|м|н|п|т|ф|ц|ч|ш|>щ|ъ|ы|ь|э|ю|я|q|x|l|k|j|m|t|w|u|v|n|q|x|l|k|j|m|t|w|u|v|n|t|w|u|v|n|t|w|u|v|n|丶|丿|亅|人|丁|二|入|八|卜|又|厂|匸|匚|勹|凵|几|冫|冖|冂|儿|亠|厶|乂|了|丁|卩|巾|山|士|己|>>凡|彳|彡|川|廾|广|巛|介|屮|尸|宀|口|囗|兀|于|个|干|爻|殳|戈|弖|夭|夬|卞|卅|从|廿|凸|凹|卍|豸|囲|因|囚|!|#|\$|%|&|\(|\)|=|\||\+|\*|\{|\}|<|>|\[|\]|\?|_|\/|\.|,|:|;|"|\'|`|~|\^|\@|\-|\\]{3,}', '', s)
    # 空白の連続
    s = re.sub(r' {2,}', '', s)
    return s

def web_tf_cache_load(web_path, output_path):
    """
    web文書のtfを取得する
    キャッシュロード
    :param doc_path:
    :param output_path:
    :return:
    """
    # web文書の読み込み
    if (os.path.exists(output_path) == False):
        web_tf_list = []
        for web_dir in ht.dir_list(web_path):
            web_str = ht.dir_read_join(web_dir, join_str=u"。")
            web_str = web_str_normalize(web_str)
            web_tc = ht.TextCollection([web_str])
            # TODO: tf()は配列を返す仕様にしてあるので1つだけの場合は先頭返してほしい
            web_tf_list.append(ht.TfIdf(web_tc).tf()[0])
        ht.pickle_save(web_tf_list, output_path)
    else :
        web_tf_list = ht.pickle_load(output_path)
    return web_tf_list

def in_stopword(char):
    """
    ストップワードが含まれているかどうか
    :param char:
    :return:
    """
    a = [u"の", u"ん", u"こと", u"よう", u"もの", u"さ", u"どれ", u"とこ", u"なん", u"それ", u"ふう", u"ほう", u"とき", u"そこ"]
    f = char in a
    return(f)

def bm25(q_word, doc_tf, idf, doc_length, avg_length, k=2.0, b=0.75):
    '''
    :param q_word: クエリのワード
    :param doc_tf: 対象ドキュメントの非正規化のtf (dict)
    :param idf:
    :param doc_length: 文書長
    :param avg_length: 平均文書長
    :param k: 
    :param b: 
    :return:
    '''
    tf_unknown = 0.0
    idf_unknown = 0.0
    score = idf.get(q_word, idf_unknown) * ( doc_tf.get(q_word, tf_unknown) * (k+1) ) / (doc_tf.get(q_word, tf_unknown) + k * ( (1-b) + b * ( doc_length / avg_length) ) )
    return score

def dd(s):
    ht.pp(s)
    exit()
    
if __name__ == '__main__':
    """
    main program
    """
    # データの設定
    conf = config.Config("web_query_likelihood")
    QUERY_PATH = conf.WRITE_QUERY_PATH
    # QUERY_PATH = conf.SPOKEN_QUERY_PATH
    DOC_PATH = conf.WRITE_DOC_PATH
    # DOC_PATH = conf.SPOKEN_DOC_LECTURE_PATH # 講演の会話データ
    # DOC_PATH = conf.WRITE_DOC_LECTURE_PATH
    DOC_CORPUS_PATH = conf.WRITE_DOC_PATH
    WEB_PATH = conf.PROJECT_PATH + "/data/formalrun-text100"

    # キャッシュ用パス
    DOC_TEXT_PATH = conf.TMP_PATH + "/doc_text"
    DOC_TF_PATH = conf.TMP_PATH + "/doc_tf"
    DOC_IDF_PATH = conf.TMP_PATH + "/doc_idf"
    QUERY_TF_PATH = conf.TMP_PATH + "/query_tf"
    WEB_TF_PATH = conf.TMP_PATH + "/web_tf"

    # 検索文書を読み込み
    doc_tc = helper.doc_text_cache_load(DOC_PATH, DOC_TEXT_PATH);
    
    # TODO: you use bm25, so normaize flag is False
    doc_tf = helper.doc_tf_cache_load(DOC_PATH, DOC_TF_PATH, normalize=False)
    doc_idf = helper.doc_idf_cache_load(DOC_PATH, DOC_IDF_PATH)
    
    # コーパスのtfを読み込み
    texts_str = doc_tc.merge_texts()
    corpus_doc_tc = ht.TextCollection([texts_str])
    corpus_doc_tf = ht.TfIdf(corpus_doc_tc).tf()[0]

    # クエリを読み込み
    q_tf_list = helper.query_tf_cache_load(QUERY_PATH, QUERY_TF_PATH, normalize=False)

    # webのtfの文書を読み込み
    web_tf_list = web_tf_cache_load(WEB_PATH, WEB_TF_PATH)
    
    # params
    tf_corpus = corpus_doc_tf.vec
    not_word_val = 1e-250 # 極小値
    u = 920 # ドキュメントコレクション用パラメータ
    v = 10 # web文書用パラメータ
    # 平均文書長
    avg_length = 121.046669042

    result = []
    # query loop
    for i, q_tf_vsm in enumerate(q_tf_list):
        query_text = q_tf_vsm.text
        query_tf = q_tf_vsm.vec
        query_result = []
        
        # queryに関係するwebのtfを計算
        tf_web = web_tf_list[i].vec

        # doc loop
        for doc_tf_vsm in doc_tf:
            doc_text = doc_tf_vsm.text
            tf_doc = doc_tf_vsm.vec
            d = len(doc_text.words())
            frac = 1.0 / float(d + u + v)
            likelifood = 0.0

            # query word loop
            for word in query_text.words():
            # for word in list(set(query_text.words())):
                # smooth for query
                # TODO: choose smooth or insert bm25
                # doc = d * frac * tf_doc.get(word, not_word_val)
                doc = d * frac * bm25(word, tf_doc, doc_idf, d, avg_length)

                # smooth for doc
                corpus = u * frac * tf_corpus.get(word, not_word_val)
                # smooth for web doc
                web = v * frac * tf_web.get(word, not_word_val)

                likelifood += log(doc + corpus + web)

            query_result.append((doc_text, likelifood))
            
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

