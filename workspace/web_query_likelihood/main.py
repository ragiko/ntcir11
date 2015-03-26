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
from math import fabs
import re

from collections import Counter
from collections import defaultdict

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

def bm25_not_idf(q_word, doc_tf, doc_length, avg_length, k=2.0, b=0.75):
    '''
    Bm25でidfが存在しない
    
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
    # score = doc_tf.get(q_word, tf_unknown)
    score = ( doc_tf.get(q_word, tf_unknown) * (k+1) ) / (doc_tf.get(q_word, tf_unknown) + k * ( (1-b) + b * ( doc_length / avg_length) ) )
    return score

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

def merge_dict(d1, d2, func=lambda x, y: y):
    '''
    辞書を足し算する
    http://tell-k.hatenablog.com/entry/2012/01/25/231445

    :param d1:
    :param d2:
    :return:
    '''
    
    d1 = d1.copy()
    d2 = d2.copy()
    for k, v in d2.iteritems():
        d1[k] = func(d1[k], v) if k in d1 else v
    d2.update(d1)
    return d2
    
def bm25_in_doc(doc_vsm_list, idf, avg_length, k=2.0, b=0.75):
    '''
    正規化のために文書全体に対してBM25を計算
    http://tell-k.hatenablog.com/entry/2012/01/25/231445

    :param doc_vsm_list: 文書のVSM型のリスト(非正規化TF)
    :param idf: 
    :param avg_length: 
    :param k: 
    :param b: 
    :return: dist {'a' => 1, 'b' => 2 ... }
    '''
    h = {}

    for doc_vsm in doc_vsm_list:
        tf = doc_vsm.vec
        text = doc_vsm.text
        doc_length = len(text.words())
        
        # bm25の文書ベクトルを作成
        bm25_dict = {}
        for word in text.words():
            bm25_dict[word] = bm25(word, tf, idf, doc_length, avg_length, k, b)
        
        h = merge_dict(h, bm25_dict, lambda x, y: x + y)
    return h

def bm25_in_a_doc(doc_vsm, avg_length, k=2.0, b=0.75):
    '''
    文書に対してbm25をすべて足す
    idfは利用しない
    
    :param doc_vsm: 
    :param avg_length: 
    :param k: 
    :param b: 
    :return: float
    '''
    tf = doc_vsm.vec
    text = doc_vsm.text
    doc_length = len(text.words())

    # 文書のbm25の全体値を計算
    sum = 0.0
    for word in list(set(text.words())): # query_words:
        sum += bm25_not_idf(word, tf, doc_length, avg_length, k, b)
    return sum

def bm25_in_a_doc_using_idf(doc_vsm, idf, avg_length, k=2.0, b=0.75):
    '''
    文書に対してbm25をすべて足す
    idfは利用しない

    :param doc_vsm:
    :param avg_length:
    :param k:
    :param b:
    :return: float
    '''
    tf = doc_vsm.vec
    text = doc_vsm.text
    doc_length = len(text.words())

    # 文書のbm25の全体値を計算
    sum = 0.0
    for word in list(set(text.words())): # query_words:
        sum += bm25(word, tf, idf, doc_length, avg_length, k, b)
    return sum


def fraction(d, u, v, defalt=True):
    '''
    文書の重みを利用するかどうかを決定
    :param d: 
    :param u: 
    :param v: 
    :param defalt: 利用しない場合, defalt=False
    :return:
    '''
    if (defalt):
        return 1.0 / float(d + u + v)
    else:
        return 1.0 / float((1-u) + u + v)

if __name__ == '__main__':
    """
    main program
    """
    # データの設定
    conf = config.Config("web_query_likelihood")
    QUERY_PATH = conf.WRITE_QUERY_PATH
    # QUERY_PATH = conf.SPOKEN_QUERY_PATH
    DOC_PATH = conf.WRITE_DOC_PATH
    
    # TODO: 講演の情報を利用したい時
    # DOC_PATH = conf.SPOKEN_DOC_LECTURE_PATH # 講演の会話データ
    # DOC_PATH = conf.WRITE_DOC_LECTURE_PATH
    
    DOC_CORPUS_PATH = conf.WRITE_DOC_PATH
    WEB_PATH = conf.PROJECT_PATH + "/data/formalrun-text100"

    # キャッシュ用パス
    # TODO: データをキャッシュしているので、不要なときは消す
    DOC_TEXT_PATH = conf.TMP_PATH + "/doc_text"
    DOC_TF_PATH = conf.TMP_PATH + "/doc_tf"
    DOC_TF_FREQ_PATH = conf.TMP_PATH + "/doc_tf_freq"
    DOC_IDF_PATH = conf.TMP_PATH + "/doc_idf"
    QUERY_TF_PATH = conf.TMP_PATH + "/query_tf"
    WEB_TF_PATH = conf.TMP_PATH + "/web_tf"

    # 検索文書を読み込み
    doc_tc = helper.doc_text_cache_load(DOC_PATH, DOC_TEXT_PATH)
    
    doc_tf = helper.doc_tf_cache_load(DOC_PATH, DOC_TF_PATH)
    # TODO: BM25を利用するときは, 非正規化(False)にする
    doc_tf_freq = helper.doc_tf_cache_load(DOC_PATH, DOC_TF_FREQ_PATH, False)

    doc_idf = helper.doc_idf_cache_load(DOC_PATH, DOC_IDF_PATH)
    
    # コーパスのtfを読み込み
    texts_str = doc_tc.merge_texts()
    corpus_doc_tc = ht.TextCollection([texts_str])
    corpus_doc_tf = ht.TfIdf(corpus_doc_tc).tf()[0]

    # クエリを読み込み
    q_tf_list = helper.query_tf_cache_load(QUERY_PATH, QUERY_TF_PATH)

    # webのtfの文書を読み込み
    web_tf_list = web_tf_cache_load(WEB_PATH, WEB_TF_PATH)
    
    # params
    tf_corpus = corpus_doc_tf.vec
    not_word_val = 1e-250 # 極小値
    
    # TODO: bm25を正規化して検索対象の重みを線形結合する場合, uを1以下
    a = 0.3 # bm25の重み
    u = 0.7 # ドキュメントコレクションの重み 920
    v = 0.0 #10 # web文書用パラメータ
    
    # 平均文書長 (hara: 47くらいか?) 121.046669042
    avg_length = 47.0 # 121.04 # 47.0
    
    # TODO: 線形結合
    # alpha = 0.05

    # TODO: bm25の正規化する時
    # bm25_in_doc = bm25_in_doc(doc_tf, doc_idf, avg_length)

    result = []
    # query loop
    for i, q_tf_vsm in enumerate(q_tf_list):
        query_text = q_tf_vsm.text
        query_tf = q_tf_vsm.vec
        query_result = []

        # queryに関係するwebのtfを計算
        tf_web = web_tf_list[i].vec

        # doc loop
        for (doc_tf_vsm, doc_tf_freq_vsm) in zip(doc_tf, doc_tf_freq):
            doc_text = doc_tf_vsm.text
            tf_doc = doc_tf_vsm.vec
            tf_freq_doc = doc_tf_freq_vsm.vec
            d = len(doc_text.words())
            # TODO: bm25を正規化して検索対象の重みを線形結合する場合, 4引数目をfalse
            frac = fraction(d, u, v, False)
            likelifood = 0.0
            
            bm25_sum = 0.0
            
            # TODO: bm25の正規化(文書全体)する時
            # bm25_all_value = bm25_in_a_doc(doc_tf_freq_vsm, avg_length)
            bm25_all_value = bm25_in_a_doc_using_idf(doc_tf_freq_vsm, doc_idf, avg_length)

            # query word loop
            for word in query_text.words():
            # for word in list(set(query_text.words())):
            
                if (in_stopword(word)):
                    continue

                # smooth for query
                # TODO: クエリ尤度のみを利用する時
                # doc = d * frac * tf_doc.get(word, not_word_val)
                # TODO: bm25を利用する時
                # doc = d * frac * bm25(word, tf_doc, doc_idf, d, avg_length)
                # doc = (1-u) * frac * bm25(word, tf_doc, doc_idf, d, avg_length)
                # TODO: bm25の正規化する時
                # doc = d * frac * bm25(word, tf_doc, doc_idf, d, avg_length) / bm25_in_doc.get(word, 1.0)
                # TODO: bm25を正規化する時, 検索対象の重みを線形結合する場合
                # doc = (1-u) * frac * bm25(word, tf_doc, doc_idf, d, avg_length) / bm25_in_doc.get(word, 1.0)
                # TODO: bm25の正規化(文書全体)する時
                if (bm25_all_value != 0.0):
                    # bm25_doc = a * frac * bm25_not_idf(word, tf_freq_doc, d, avg_length) / bm25_all_value
                    bm25_doc = a * frac * bm25(word, tf_freq_doc, doc_idf, d, avg_length) / bm25_all_value
                else:
                    bm25_doc = 0.0

                # TODO: 追加
                query_likelifood_doc = (1-u-a) * frac * tf_doc.get(word, not_word_val)

                # doc = a * frac * bm25(word, tf_freq_doc, doc_idf, d, avg_length)
                # bm25_sum += bm25(word, tf_freq_doc, doc_idf, d, avg_length)

                # smooth for doc
                corpus = u * frac * tf_corpus.get(word, not_word_val)
                # smooth for web doc
                web = v * frac * tf_web.get(word, not_word_val)
            
                # print "\n"
                # print "corpus: " + word.encode('utf8') + " : " + str(corpus)
                # print "web: " + word.encode('utf8') + " : " + str(web)

                likelifood += log(query_likelifood_doc + bm25_doc + corpus + web)

                # TODO: 線形結合
                # likelifood += alpha*bm25(word, tf_doc, doc_idf, d, avg_length) + (1-alpha)*log(doc + corpus + web)
                
                # print "bm25\n"
                # ht.pp(sorted(t1_hs.items(), key=lambda x:x[1]))
                # print "query 尤度\n"
                # ht.pp(sorted(t2_hs.items(), key=lambda x:x[1]))

            query_result.append((doc_text, likelifood))
            # query_result.append((doc_text, bm25_sum))

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

