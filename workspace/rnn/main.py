#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from os.path import basename
import hymlab.text as ht

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../helper')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../config')
import helper
import config

from math import log
import re

import pickle
import codecs

# -----------------------------------------------------------------------
# 日本語を含む文字列を標準入出力とやり取りする場合に書く
# UTF-8の文字列を標準出力に出力したり，標準入力から入力したりできるようになる
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)
# デフォルトのエンコーディングを変更する
reload(sys)
sys.setdefaultencoding('utf-8')
# -----------------------------------------------------------------------


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

def web_slide_tf_dump(web_path, output_path):
    """
    web文書のtfを取得する
    キャッシュロード
    :param doc_path:
    :param output_path:
    :return:
    """
    # dump
    i = 0
    paths = os.listdir(output_path)
    if (len(paths) == 0):
        for web_dir in ht.dir_list(web_path):
            web_str = ht.dir_read_join(web_dir, join_str=u"。")
            web_str = web_str_normalize(web_str)
            web_tc = ht.TextCollection([web_str])

            path = output_path + "/" + slide_path_format(web_dir)
            # TODO: tf()は配列を返す仕様にしてあるので1つだけの場合は先頭返してほしい
            slide_tf = ht.TfIdf(web_tc).tf()[0]
            ht.pickle_save(slide_tf, path)

            i += 1
            ht.pp(i)
    return

def web_slide_tf_load(web_output_path):
    '''
    slideのデータを1スライド単位で取得

    :param web_output_path: スライドの解析データが保存されいる先
    :return:
    '''

    vsm = ht.pickle_load(web_output_path)
    return vsm

def web_all_slide_tf_load(web_dir):
    '''
    slideのデータを全てのスライド単位で取得

    :param web_output_path: スライドの解析データが保存されいるディレクトリ
    :return:
    '''

    h = {}
    for web_path in os.listdir(web_dir):
        h[slide_path_format(web_path)] = ht.pickle_load(web_dir+"/"+web_path)
    return h

def in_stopword(char):
    """
    ストップワードが含まれているかどうか
    :param char:
    :return:
    """
    a = [u"の", u"ん", u"こと", u"よう", u"もの", u"さ", u"どれ", u"とこ", u"なん", u"それ", u"ふう", u"ほう", u"とき", u"そこ"]
    f = char in a
    return(f)

def in_stopword_using_re(char):
    '''
    ストップワードを正規表現で設定

    :param path:
    :return: str
    '''

    # 半角全角記号のみ
    a = re.search('[!-/:-@[-`{-~、-◯]', char)
    # 数字が1文字または2文字
    b = re.search('\d{1,2}', char)
    if a or b:
        return True
    else:
        return False


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

def slide_path_format(path):
    '''
    スライドの絶対パスからディレクトリ名だけ取得
    :param path:
    :return: str
    '''
    path = basename(path)
    m = re.search('^(\d+-\d+_\d+).*$', path)
    if m:
        return m.group(1)
    else:
        return ""

def sim_bitween_web_and_docs(web_vsm, doc_vsm_list):
    '''
    web文書と検索文書全体の類似度

    :param web_vsm:
    :param doc_vsm_list:
    :return:
    '''
    sim = ht.Similarity(doc_vsm_list)
    sim_all_doc = sim.most_similarity_by_feature(web_vsm)

    sum = 0.0
    for sim_doc in sim_all_doc:
        if sim_doc.similarity is None:
            continue
        sum += sim_doc.similarity
    return (sum/len(sim_all_doc))



def get_rnn_result():
    '''
    RNNの結果（ボキャブラリーと確率分布）を取得する
    '''

    # ボキャブラリーのロード
    f_voc = open("/home/ogawa/NTCIR-12/RNN_result/vocab.bin", "rb")
    vocab = pickle.load(f_voc)
    ivocab = {} # ボキャブラリー（学習データの全単語）とIDの対応付け
    for c, i in vocab.items():
        ivocab[i] = c

    # ivocabのキーとバリューを入れ替える
    ivocab_inv = {v:k for k, v in ivocab.items()}

    # 確率分布のロード
    f_prob = open("/home/ogawa/NTCIR-12/RNN_result/probability_list_data.txt", "rb")
    prob_list = pickle.load(f_prob)

    prob_slide = []

    for lecture in range(len(prob_list)):
        for slide in range(len(prob_list[lecture])):
            prob_slide.append(prob_list[lecture][slide])


    # print prob_slide[0][0]
    # print prob_slide[0][ivocab_inv[u"水車"]]
    # sys.exit()

    return ivocab_inv, prob_slide



if __name__ == '__main__':
    """
    main program
    """
    # データの設定
    conf = config.Config("rnn")
    # QUERY_PATH = conf.WRITE_QUERY_PATH
    QUERY_PATH = conf.SPOKEN_QUERY_PATH
    # DOC_PATH = conf.WRITE_DOC_PATH
    DOC_PATH = conf.SPOKEN_K_DOC_PATH

    # DOC_CORPUS_PATH = conf.WRITE_DOC_PATH
    DOC_CORPUS_PATH = conf.SPOKEN_K_DOC_PATH
    # WEB_PATH = conf.PROJECT_PATH + "/data/formalrun-check100"

    # キャッシュ用パス
    # TODO: データをキャッシュしているので、不要なときは消す
    DOC_TEXT_PATH = conf.TMP_PATH + "/doc_text"
    DOC_TF_PATH = conf.TMP_PATH + "/doc_tf"
    DOC_TF_FREQ_PATH = conf.TMP_PATH + "/doc_tf_freq"
    DOC_IDF_PATH = conf.TMP_PATH + "/doc_idf"
    QUERY_TF_PATH = conf.TMP_PATH + "/query_tf"
    # WEB_TF_PATH = conf.TMP_PATH + "/web_slide"
    # DOC_WEB_SIM_PATH = conf.TMP_PATH + "/doc_web_sim"

    # 検索文書, TF-IDFを読み込み
    doc_tc = helper.doc_text_cache_load(DOC_PATH, DOC_TEXT_PATH)
    doc_tf = helper.doc_tf_cache_load(DOC_PATH, DOC_TF_PATH)
    doc_tf_freq = helper.doc_tf_cache_load(DOC_PATH, DOC_TF_FREQ_PATH, False)
    doc_idf = helper.doc_idf_cache_load(DOC_PATH, DOC_IDF_PATH)

    # コーパスのTFを読み込み
    texts_str = doc_tc.merge_texts()
    corpus_doc_tc = ht.TextCollection([texts_str])
    corpus_doc_tf = ht.TfIdf(corpus_doc_tc).tf()[0]

    # クエリを読み込み
    q_tf_list = helper.query_tf_cache_load(QUERY_PATH, QUERY_TF_PATH)

    # webのtfの文書を読み込み
    # web_tf_list = web_tf_cache_load(WEB_PATH, WEB_TF_PATH)

    # RNN関係を読み込み
    ivocab_inv = {}
    prob_slide = []
    ivocab_inv, prob_slide = get_rnn_result()

    print "########################################\n"
    print "# web slide loaded %s\n"
    print "########################################\n"

    tf_corpus = corpus_doc_tf.vec
    not_word_val = 1e-250 # 極小値
    u = 320 # ドキュメントコレクションの重み 920
    v = 10.0 # web文書用パラメータ (10)

    slide_num = 0 # 何個目のスライドか記憶する

    result = []
    # query loop
    for i, q_tf_vsm in enumerate(q_tf_list):

        print "########################################"
        print "# query ", i
        print "########################################"

        query_text = q_tf_vsm.text
        query_tf = q_tf_vsm.vec
        query_result = []

        # queryに関係するwebのtfを計算
        tf_web = web_tf_list[i].vec

        # doc loop (スライド単位のはず)
        for (doc_tf_vsm, doc_tf_freq_vsm) in zip(doc_tf, doc_tf_freq):

            doc_text = doc_tf_vsm.text
            # slide文書のロード先
            doc_path = slide_path_format(doc_tf_vsm.text.path)

            tf_doc = doc_tf_vsm.vec
            tf_freq_doc = doc_tf_freq_vsm.vec

            d = len(doc_text.words())
            frac = 1.0 / float(d + u + v)
            likelifood = 0.0

            # query word loop
            for word in query_text.words():

                if (in_stopword(word) or in_stopword_using_re(word)):
                    continue

                # smooth for query
                doc = d * frac * tf_doc.get(word, not_word_val) # スライド
                # smooth for doc
                corpus = u * frac * tf_corpus.get(word, not_word_val) # 講演全体をつなげたもの
                try:
                    rnn = v * frac * prob_slide[slide_num][ivocab_inv[word]]
                except:
                    rnn = not_word_val
                    # print word, "を無視します"

                likelifood += log(doc + corpus + rnn)


                # # smooth for query
                # doc = d * frac * tf_doc.get(word, not_word_val) # スライド
                # # smooth for doc
                # corpus = u * frac * tf_corpus.get(word, not_word_val) # 講演全体をつなげたもの
                # # smooth for web doc
                # # web = v * frac * tf_web.get(word, not_word_val) # Web文書 ここをRNNに変えてみる


                # likelifood += log(doc + corpus + web)

            query_result.append((doc_text, likelifood))
            slide_num += 1
        result.append(query_result)
        slide_num = 0


    helper.output_result(result, conf.RESULT_PATH)
    print "########################################"
    print "# 出力完了 " + conf.RESULT_PATH
    print "########################################"

