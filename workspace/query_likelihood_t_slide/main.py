#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import hymlab.text as ht

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../helper')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../config')
import helper
import config
from math import log
import re

def in_stopword(char):
    """
    ストップワードが含まれているかどうか
    :param char:
    :return:
    """
    a = [u"の", u"ん", u"こと", u"よう", u"もの", u"さ", u"どれ", u"とこ", u"なん", u"それ", u"ふう", u"ほう", u"とき", u"そこ"]
    f = char in a
    return(f)

def dd(s):
    ht.pp(s)
    exit()
    
def select_tf_by_lecture_id(lecture_tf, lecture_id):
    a = [l for l in lecture_tf if re.search(lecture_id, l.text.path)]
    if (len(a) == 1):
        return a[0]
    return null

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
    else:
        web_tf_list = ht.pickle_load(output_path)
    return web_tf_list

if __name__ == '__main__':
    """
    main program
    """
    # データの設定
    conf = config.Config("query_likelihood_t_slide")
    QUERY_PATH = conf.WRITE_QUERY_PATH
    # QUERY_PATH = conf.SPOKEN_QUERY_PATH
    DOC_PATH = conf.WRITE_DOC_PATH
    
    # TODO: 講演の情報を利用したい時
    # DOC_PATH = conf.SPOKEN_DOC_LECTURE_PATH # 講演の会話データ
    LECTURE_PATH = conf.WRITE_DOC_LECTURE_PATH
    
    DOC_CORPUS_PATH = conf.WRITE_DOC_PATH
    WEB_PATH = conf.PROJECT_PATH + "/formalrun-text100"

    # キャッシュ用パス
    # TODO: データをキャッシュしているので、不要なときは消す
    DOC_TEXT_PATH = conf.TMP_PATH + "/doc_text"
    DOC_TF_PATH = conf.TMP_PATH + "/doc_tf"
    DOC_TF_FREQ_PATH = conf.TMP_PATH + "/doc_tf_freq"
    DOC_IDF_PATH = conf.TMP_PATH + "/doc_idf"
    QUERY_TF_PATH = conf.TMP_PATH + "/query_tf"
    LECTURE_TF_PATH = conf.TMP_PATH + "/lecture_tf"
    WEB_TF_PATH = conf.TMP_PATH + "/web_tf"

    # 検索文書を読み込み
    doc_tc = helper.doc_text_cache_load(DOC_PATH, DOC_TEXT_PATH)
    doc_tf = helper.doc_tf_cache_load(DOC_PATH, DOC_TF_PATH)
    doc_tf_freq = helper.doc_tf_cache_load(DOC_PATH, DOC_TF_FREQ_PATH, False)
    doc_idf = helper.doc_idf_cache_load(DOC_PATH, DOC_IDF_PATH)
    lecture_tf = helper.doc_tf_cache_load(LECTURE_PATH, LECTURE_TF_PATH)

    # コーパスのtfを読み込み
    texts_str = doc_tc.merge_texts()
    corpus_doc_tc = ht.TextCollection([texts_str])
    corpus_doc_tf = ht.TfIdf(corpus_doc_tc).tf()[0]

    # webのtfの文書を読み込み
    web_tf_list = web_tf_cache_load(WEB_PATH, WEB_TF_PATH)

    # クエリを読み込み
    q_tf_list = helper.query_tf_cache_load(QUERY_PATH, QUERY_TF_PATH)

    # params
    tf_corpus = corpus_doc_tf.vec
    not_word_val = 1e-250 # 極小値
    
    # ドキュメントコレクションの重み
    a = 0.5

    result = []
    # query loop
    for i, q_tf_vsm in enumerate(q_tf_list):
        ht.pp("- query" + str(i) )

        query_text = q_tf_vsm.text
        query_tf = q_tf_vsm.vec
        query_result = []

        # queryに関係するwebのtfを計算
        tf_web = web_tf_list[i].vec

        # doc loop
        for (doc_tf_vsm, doc_tf_freq_vsm) in zip(doc_tf, doc_tf_freq):
            
            doc_text = doc_tf_vsm.text
            # スライドに文字が無い時
            if (len(doc_text.words()) == 0):
                continue

            tf_doc = doc_tf_vsm.vec
            tf_freq_doc = doc_tf_freq_vsm.vec

            m = re.search(".*(\d{2}-\d{2}).*$" , doc_text.path)
            lecture_id = m.group(1)
            select_lecture_tf = select_tf_by_lecture_id(lecture_tf, lecture_id)
            
            # s = スライド
            # d = 講演
            
            # p(s=スライド|d=講演)
            # 事前に分かっている (=1)
            s_d_likelifood = 0.0

            # p(q=クエリ|s=スライド)
            q_s_likelifood = 0.0
            for word in query_text.words():

                if (in_stopword(word)):
                    continue
                    
                doc = (1-a) * tf_doc.get(word, not_word_val)
                corpus = a * tf_corpus.get(word, not_word_val)
                q_s_likelifood += log(doc + corpus)

            # p(q=クエリ|d=講演)
            q_d_likelifood = 0.0
            for word in query_text.words():

                if (in_stopword(word)):
                    continue

                doc = (1-a) * select_lecture_tf.vec.get(word, not_word_val)
                corpus = a * tf_corpus.get(word, not_word_val)
                q_d_likelifood += log(doc + corpus)

            likelifood = q_s_likelifood + q_d_likelifood + web_likelifood

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

