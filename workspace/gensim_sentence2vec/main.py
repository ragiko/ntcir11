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

class LabeledLineSentence(object):
    """
    doc2vecのモデル用のモデル

    textcollection と label は他のオブジェクトに依存しない
    """
    def __init__(self, textcollection, label):
        self.textcollection = textcollection 
        self.label = label 
        self.sentences_cache = None

    def __add__(self, labeled_line_sentence):
       sents = LabeledLineSentence(None, None)
       sents.sentences_cache = self.sentences() + labeled_line_sentence.sentences()
       return sents

    def __iter__(self):
        for sent in self.sentences():
            yield sent

    def __len__(self):
        return len(self.sentences())

    def sentences(self):
        """
        sentence2vecのモデルに渡す用のsent
        """
        if self.sentences_cache is not None:
            return self.sentences_cache

        sentences = []

        print "start word parse"
        lines = self.textcollection.words_list([u"名詞", u"動詞", u"形容詞", u"副詞"]) # すべての形態素
        # lines = self.textcollection.words_list([u"名詞"]) # すべての形態素

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
        # self.expand_tc = ht.TextCollection([text.text() for text in self.expand_tc.list()])
        # self.all_tc = self.query_tc + self.doc_tc + self.expand_tc  

        self.doc_sents = LabeledLineSentence(self.doc_tc, "DOC")
        self.query_sents = LabeledLineSentence(self.query_tc, "QUERY")
        self.expand_sents = LabeledLineSentence(self.expand_tc, "EXPAND")

    def make_corpus(self):
        self.query_tc.add_text_collection(self.doc_tc)
        merge_tc = self.query_tc
        merge_tc.dump_corpus(self.corpus_path)

    def make_train_sentences(self):
        return self.expand_sents 

    def make_test_sentences(self):
        return self.doc_sents + self.query_sents

    def make_sent2vec_sentences(self):
        return self.doc_sents + self.query_sents + self.expand_sents

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
        self.test_sentences = self.corpus.make_test_sentences() 
        self.train_sentences = self.corpus.make_train_sentences() 
        self.model_cache = None

    def model(self):
        if self.model_cache is not None:
            return self.model_cache
        return self.train()

    def train(self, _size=400, _min_count=9, _window=8, _sample=0.0, _dm=1):
        """
        LabeledLineSentenceに
            trainデータ
            testデータ
        を保有させる

        trainデータとtestデータを分けたい
        """
        epoch = 1

        # モデル作成
        model = Doc2Vec(size=_size, window=_window, min_count=_min_count, workers=4, sample=_sample, dm=_dm)
        model.build_vocab(self.sentences)

        # that's too bad
        print "all data size (%s)" % str(len(self.sentences))

        # wordvectorのみ学習
        model.train_words = True
        model.train_lbls = False
        for i in range(epoch):
            model.train(self.train_sentences)
            print "train data size (%s)" % str(len(self.train_sentences))

        # word2vecの重みを止める
        model.train_words = False
        model.train_lbls = True
        for i in range(epoch):
            model.train(self.test_sentences)
            print "train data size (%s)" % str(len(self.test_sentences))

        # model = Doc2Vec(alpha=0.025, min_alpha=0.025, workers=4)  # use fixed learning rate
        # model.build_vocab(self.sentences)
        #  
        # for epoch in range(1):
        #     model.train(self.sentences)
        #     model.alpha -= 0.002  # decrease the learning rate
        #     model.min_alpha = model.alpha  # fix the learning rate, no decay

        # trainはモデルの値を更新
        self.model_cache = model
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
    LOAD_MODE = False 

    # extra data 100
    SAVE_NAME_PATH = MIDDLE_PATH + "/save_extra_data_100" 
    # extra data 10000
    # SAVE_NAME_PATH = MIDDLE_PATH + "/save" 
    # extra data all
    # SAVE_NAME_PATH = MIDDLE_PATH + "/save_extra_data_all" 

    # ////////////////////
    # if model load
    # ////////////////////

    if (LOAD_MODE):
        model = mysentvec_load(SAVE_NAME_PATH)
        model.train()

    # ////////////////////
    # if make model
    # ////////////////////

    if (LOAD_MODE == False):
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

    # fileのアウトプット
    helper.output_result(res, conf.RESULT_PATH)
