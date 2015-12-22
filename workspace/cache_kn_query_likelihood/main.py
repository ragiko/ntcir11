#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import hymlab.text as ht

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../helper')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../config')
from math import log
import helper
import config
import re
from os.path import basename

import copy
import knlm

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

# wordのキャッシュリスト
def queue_list(arr, ele, max=80):
    a = list(arr)
    a.append(ele)
    if len(a) > max:
        a.pop(0)
    return a

# tfidf.pyから拝借
# 頻度を取得
def calc_tf_vec(text, normalize=False):
    """
    vec (dist型) で返却する
    calc_tfではcount()が遅いため
    """
    vec = {}
    for word in text:
        vec[word] = vec.get(word, 0) + 1

    if (normalize):
        l = len(text)
        return {k:(float(v)/float(l)) for k, v in vec.items()}
    else:
        return vec

def norm_vec(dict):
    """
    ベクトルを長さで正規化
    tf => 確率に
    """
    sum = 0.0
    for v in dict.values():
        sum += v
    return {k:(float(v)/float(sum)) for k, v in dict.items()}

def is_diff_lec(s1, s2):
    '''
    スライド２つに対して、同じ講演かどうか?

    :param s1: スライドid1
    :param s2: 
    :return:
    '''
    m = re.search('^(\d+-\d+)_\d+.*$', s1)
    lec1 = m.group(1)
    
    m = re.search('^(\d+-\d+)_\d+.*$', s2)
    lec2 = m.group(1)
    
    return lec1 != lec2


if __name__ == '__main__':
    
    """
    main program
    """
    # データの設定
    conf = config.Config("cache_kn_query_likelihood")
    # QUERY_PATH = conf.WRITE_QUERY_PATH
    QUERY_PATH = conf.SPOKEN_QUERY_PATH
    DOC_PATH = conf.SPOKEN_KALDI_DOC_PATH
    DOC_CORPUS_PATH = conf.SPOKEN_KALDI_DOC_PATH

    DOC_TEXT_PATH = conf.TMP_PATH + "/doc_text"
    DOC_TF_PATH = conf.TMP_PATH + "/doc_tf"
    DOC_TF_FREQ_PATH = conf.TMP_PATH + "/doc_tf_freq"
    DOC_IDF_PATH = conf.TMP_PATH + "/doc_idf"
    QUERY_TF_PATH = conf.TMP_PATH + "/query_tf"

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

    print "########################################\n"
    print "# web slide loaded %s\n"
    print "########################################\n"
    
    tf_corpus = corpus_doc_tf.vec
    not_word_val = 1e-250 # 極小値
    # ドキュメントコレクションの重み 920
    u = 320
    v = 10
    
    # キャッシュモデルの設定
    h_words = []
    history_max = 100
    old_doc_path = "07-01_000"

    # n-gram (kn smooth)の設定
    ngram = knlm.NGram(5)
    gen = knlm.Generator(ngram)
    gen_cp = copy.deepcopy(gen)
    D = 0.5 # discount
    
    cnt = 0

    result = []
    # query loop
    for i, q_tf_vsm in enumerate(q_tf_list):

        print "########################################"
        print "# query ", i
        print "########################################"
        
        query_text = q_tf_vsm.text
        query_tf = q_tf_vsm.vec
        query_result = []

        # doc loop
        for (doc_tf_vsm, doc_tf_freq_vsm) in zip(doc_tf, doc_tf_freq):
            doc_text = doc_tf_vsm.text
            # slide文書のロード先
            doc_path = slide_path_format(doc_tf_vsm.text.path)

            tf_doc = doc_tf_vsm.vec
            tf_freq_doc = doc_tf_freq_vsm.vec

            d = len(doc_text.words())
            frac = 1.0 / float(d + u + v)
            likelifood = 0.0
            
            if (is_diff_lec(doc_path, old_doc_path)):
                h_words = []

            history_vec = helper.merge_dict(tf_freq_doc, calc_tf_vec(h_words), lambda x, y: x + y)
            history_vec = norm_vec(history_vec)

            # 文書のn-gramの学習 ()
            gen.start()
            for (i, w) in enumerate(doc_text.words() + h_words):
            # for (i, w) in enumerate(doc_text.words()):
                gen.inc(w)

            # query word loop
            for word in query_text.words():

                if (in_stopword(word) or in_stopword_using_re(word)):
                    continue
                    
                # n-gram確率を計算
                voca, kn_prob = gen.ngram.probKN(D, word)
                try:
                    id = voca.index(word)
                    kn_p = kn_prob[id]
                except:
                    kn_p = not_word_val

                # smooth for query
                doc = d * frac * tf_doc.get(word, not_word_val)
                # smooth for doc
                corpus = u * frac * tf_corpus.get(word, not_word_val)
                
                # cache model
                cache = v * frac * (0.25 * kn_p + 0.75 * history_vec.get(word, not_word_val))

                likelifood += log(doc + corpus + cache)
            
            query_result.append((doc_text, likelifood))

            # 単語をキャッシュ
            for w in doc_text.words():
                h_words = queue_list(h_words, w, history_max)
            # 講演の情報を保存
            old_doc_path = doc_path
            
            # n-gramモデルのクリア
            del gen
            gen = copy.deepcopy(gen_cp)

        result.append(query_result)

    if (len(sys.argv) >= 2 and sys.argv[1]):
        helper.output_result_by_id(result, conf.RESULT_PATH, sys.argv[1])
    else:
        helper.output_result_by_id(result, conf.RESULT_PATH, "default")

    # helper.output_result(result, conf.RESULT_PATH)
    print "########################################"
    print "# 出力完了 " + conf.RESULT_PATH
    print "########################################"

