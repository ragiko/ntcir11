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

if __name__ == '__main__':
    """
    main program
    """
    # データの設定
    conf = config.Config("web_query_likelihood")
    QUERY_PATH = conf.WRITE_QUERY_PATH
    DOC_PATH = conf.WRITE_DOC_PATH
    DOC_CORPUS_PATH = conf.WRITE_DOC_PATH
    WEB_PATH = conf.PROJECT_PATH + "/data/formalrun-check100"
    
    # ドキュメントを読み込み
    doc_tc = ht.TextCollection(DOC_PATH)
    doc_tf = ht.TfIdf(doc_tc).tf()

    # クエリを読み込み
    query = ht.file_read(QUERY_PATH).split("\n")
    query.pop()
    q_tc = ht.TextCollection(query)
    
    
    q_tf_list = ht.TfIdf(q_tc).tf(normalize=False)
    
    # ht.pp(q_tf_list)

    # web文書の読み込み
    web_tf_list = []
    for web_dir in ht.dir_list(WEB_PATH):
        web_str = ht.dir_read_join(web_dir, join_str=u"。")
        web_str = web_str_normalize(web_str)
        web_tc = ht.TextCollection([web_str])
        # TODO: tf()は配列を返す仕様にしてあるので1つだけの場合は先頭返してほしい
        web_tf_list.append(ht.TfIdf(web_tc).tf()[0])

    #  コーパスのtf
    # doc_tc = ht.TextCollection(DOC_CORPUS_PATH)
    texts_str = doc_tc.merge_texts()
    corpus_doc_tc = ht.TextCollection([texts_str])
    corpus_doc_tf = ht.TfIdf(corpus_doc_tc).tf()[0]

    # params
    # 平均文書長 121.046669042
    tf_corpus = corpus_doc_tf.vec
    not_word_val = 1e-50 # 極小値
    u = 160 # ドキュメントコレクション用パラメータ
    v = 50 # web文書用パラメータ

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
                # smooth for query
                doc = d * frac * tf_doc.get(word, not_word_val)
                # smooth for doc
                corpus = u * frac * tf_corpus.get(word, not_word_val)
                # smooth for web doc
                web = v * frac * tf_web.get(word, not_word_val)

                likelifood += query_tf[word] * log(doc + corpus + web)

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

