#!/usr/bin/python
# -*- coding: utf-8 -*-

import hymlab.text as ht
from gensim.models.doc2vec import *

class LabeledLineSentence(object):
    """
    doc2vecのモデル用のモデル
    """
    def __init__(self, filename, labelname):
        self.filename = filename
        self.labelname = labelname
        self.sentences_cache = None
 
    def sentences(self):
        """
        sentence2vecのモデルに渡す用のsent
        """
        if self.sentences_cache is not None:
            return self.sentences_cache

        sentences = []
        lines = ht.file_read(self.filename).split("\n")
        for uid, line in enumerate(lines):
            sentences.append(LabeledSentence(words=line.split(), labels=['%s_%s' % (self.labelname, str(uid))]))

        self.sentences_cache = sentences 
        return self.sentences_cache

    def output_sentences(self):
        for sent in self.sentences():
            ht.pp("words: ")
            ht.pp(sent.words)
            print "\n"
            ht.pp("label: %s" % sent.labels)

if __name__ == '__main__':
    WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
    TMP_DIR_PATH = WORKSPACE_DIR + "/middle" 

    labelsentences = LabeledLineSentence("%s/corpus.txt" % TMP_DIR_PATH, "SENT")
    labelsentences.output_sentences()
    sentences = labelsentences.sentences() 

