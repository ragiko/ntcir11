#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, codecs
import re 

import hymlab.text as ht
from gensim.models.doc2vec import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../helper')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../config')
import helper
import config

# 日本語を標準出力できるように
sys.stdout = codecs.getwriter("utf_8")(sys.stdout)

"""
エラーを治そう
"""

class LabeledLineSentence(object):
    """
    doc2vecのモデル用のモデル
    """
    def __init__(self, textcollection, label):
        self.textcollection = textcollection 
        self.label = label 
        self.sentences_cache = None

    def __add__(self, labeled_line_sentence):
       self.sentences_cache = self.sentences() + labeled_line_sentence.sentences()
       return self

    def __iter__(self):
        for sent in self.sentences():
            yield sent
 
    def sentences(self):
        """
        sentence2vecのモデルに渡す用のsent
        """
        if self.sentences_cache is not None:
            return self.sentences_cache

        sentences = []

        print "start word parse"
        lines = self.textcollection.words_list([u"名詞", u"動詞"]) # すべての形態素

        print "start add labeldsentence"
        for uid, line in enumerate(lines):
            sentences.append(LabeledSentence(words=line, labels=['SENT_%s_%s' % (self.label, str(uid))]))

        self.sentences_cache = sentences 
        return self.sentences_cache

    def output_sentences(self):
        for sent in self.sentences():
            ht.pp("label: %s" % sent.labels)
            ht.pp("words: ")
            ht.pp(sent.words)
            print "\n"

class Corpus(object):
    def __init__(self):
        self.conf = config.Config("gensim_sentence2vec")
        self.corpus_path = self.conf.PROJECT_PATH+"/middle/corpus.txt"

        query = ht.file_read(self.conf.WRITE_QUERY_PATH).split("\n")
        query.pop()
        self.query_tc = ht.TextCollection(query)
        self.doc_tc = ht.TextCollection(self.conf.WRITE_DOC_PATH)
        # TODO: wrapも取れるように設計しよう...
        self.expand_tc = ht.TextCollection(self.conf.PROJECT_PATH+"/extract")
        self.expand_tc = ht.TextCollection([text.text() for text in self.expand_tc.list()[0:100]])
        self.all_tc = self.query_tc + self.doc_tc + self.expand_tc  

    def make_corpus(self):
        self.query_tc.add_text_collection(self.doc_tc)
        merge_tc = self.query_tc
        merge_tc.dump_corpus(self.corpus_path)

    def make_sent2vec_sentences(self):
        return LabeledLineSentence(self.doc_tc, "DOC") \
               + LabeledLineSentence(self.query_tc, "QUERY") \
               + LabeledLineSentence(self.expand_tc, "EXPAND")

    def doclabel2text(self, doclabel):
        """
        TODO: ちゃんとtextオブジェクトが取得しているかどうかを調べる
        """
        m = re.search('DOC_(.*)$', doclabel)
        if m:
            return self.doc_tc[int(m.group(1))]
        else: 
            return None

def mysentvec_load(fname):
    """
    mysentvecのローダー
    """
    corpus = ht.pickle_load(fname + ".corpus")
    m = MySentVec(corpus)

    sentences = ht.pickle_load(fname + ".sentences")
    model_cache = Doc2Vec.load(fname + ".model")

    m.sentences = sentences 
    m.model_cache = model_cache 

    return m

class MySentVec(object):
    def __init__(self, corpus):
        self.corpus = corpus
        self.sentences = self.corpus.make_sent2vec_sentences() 
        self.model_cache = None

    def model(self):
        if self.model_cache is not None:
            return self.model_cache

        # モデル作成
        model = Doc2Vec(self.sentences, size=400, window=5, min_count=5, workers=4)
        # model = Doc2Vec(alpha=0.025, min_alpha=0.025, workers=4)  # use fixed learning rate
        # model.build_vocab(self.sentences)
        #  
        # for epoch in range(1):
        #     model.train(self.sentences)
        #     model.alpha -= 0.002  # decrease the learning rate
        #     model.min_alpha = model.alpha  # fix the learning rate, no decay

        self.model_cache = model
        return self.model_cache

    def update(self):
        self.model_cache = Doc2Vec(self.sentences, size=400, window=5, min_count=5, workers=4)
        return self.model_cache 

    def most_similar_in_doc(self, search_label, topn=1000):
        similaries = self.model().most_similar(search_label, topn=len(self.model().syn0))
        similaries = [(self.corpus.doclabel2text(label), sim) for label, sim in similaries if self.corpus.doclabel2text(label) is not None]
        return similaries[0:topn]

    def save(self, fname):
        ht.pickle_save(self.corpus, fname + ".corpus")
        ht.pickle_save(self.sentences, fname + ".sentences")
        self.model().save(fname + ".model")

if __name__ == '__main__':

    conf = config.Config("gensim_sentence2vec")
    MIDDLE_PATH = conf.PROJECT_PATH + "/middle"

    # extra data 100
    SAVE_NAME_PATH = MIDDLE_PATH + "/save_extra_data_100" 
    # extra data 10000
    # SAVE_NAME_PATH = MIDDLE_PATH + "/save" 

    # ////////////////////
    # if model load
    # ////////////////////

    # model = mysentvec_load(SAVE_NAME_PATH)
    # model.update()

    # ////////////////////
    # if make model
    # ////////////////////

    print "make corpus"
    corpus = Corpus()

    print "make model"
    model = MySentVec(corpus)
    model.save(SAVE_NAME_PATH)

    # ////////////////////
    # calc result
    # ////////////////////

    res = []
    for i in range(37):
        query_label = "SENT_QUERY_%s" % str(i)
        res.append(model.most_similar_in_doc(query_label))

    # for text, sim in res[0][0:10]:
    #     ht.pp(text.path)
    #     ht.pp(sim)
    # 
    # fileのアウトプット
    helper.output_result(res, conf.RESULT_PATH)
