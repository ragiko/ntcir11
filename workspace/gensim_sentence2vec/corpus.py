#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import re 

import hymlab.text as ht
from gensim.models.doc2vec import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../helper')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../config')
import helper
import config

class LabeledLineSentence(object):
    """
    doc2vecのモデル用のモデル
    """
    def __init__(self, textcollection, label):
        self.textcollection = textcollection 
        self.label = label 
        self.sentences_cache = None

    def __add__(self, labeled_line_sentence):
        return self.sentences() + labeled_line_sentence.sentences()
 
    def sentences(self):
        """
        sentence2vecのモデルに渡す用のsent
        """
        if self.sentences_cache is not None:
            return self.sentences_cache

        sentences = []
        lines = self.textcollection.words_list([]) # すべての形態素
        for uid, line in enumerate(lines):
            sentences.append(LabeledSentence(words=line, labels=['SENT_%s_%s' % (self.label, str(uid))]))

        self.sentences_cache = sentences 
        return self.sentences_cache

    def output_sentences(self):
        for sent in self.sentences():
            ht.pp("words: ")
            ht.pp(sent.words)
            print "\n"
            ht.pp("label: %s" % sent.labels)

class Corpus(object):
    def __init__(self):
        self.conf = config.Config("gensim_sentence2vec")

        query = ht.file_read(self.conf.SPOKEN_QUERY_PATH).split("\n")
        query.pop()
        self.query_tc = ht.TextCollection(query)
        self.doc_tc = ht.TextCollection(self.conf.SPOKEN_DOC_PATH)

        self.corpus_path = self.conf.PROJECT_PATH+"/middle/corpus.txt"

    def make_corpus(self):
        self.query_tc.add_text_collection(self.doc_tc)
        merge_tc = self.query_tc
        merge_tc.dump_corpus(self.corpus_path)

    def make_sent2vec_sentences(self):
        return LabeledLineSentence(self.query_tc, "QUERY") \
                + LabeledLineSentence(self.doc_tc, "DOC")

class MySentVec(object):
    def __init__(self, sentences):
        self.sentences = sentences
        self.model_cache = None

    def model(self):
        if self.model_cache is not None:
            return self.model_cache

        # モデル作成
        # model = Doc2Vec(sentences, size=100, window=8, min_count=5, workers=4)
        model = Doc2Vec(alpha=0.025, min_alpha=0.025, workers=4)  # use fixed learning rate
        model.build_vocab(self.sentences)
         
        for epoch in range(1):
            model.train(self.sentences)
            model.alpha -= 0.002  # decrease the learning rate
            model.min_alpha = model.alpha  # fix the learning rate, no decay

        self.model_cache = model
        return self.model_cache

    def most_similar_in_doc(self, search_label, topn=1000):
        similaries = self.model().most_similar(search_label, topn=len(self.model().syn0))
        similaries = [(label, sim) for label, sim in similaries if re.search("DOC", label)]
        return similaries[0:topn]

if __name__ == '__main__':
    corpus = Corpus()
    model = MySentVec(corpus.make_sent2vec_sentences())
    print model.most_similar_in_doc("SENT_QUERY_0")

    # あとはコーパスがlabel2textの関数を返すだけ 
    # corpusはクエリラベル複数を返す

