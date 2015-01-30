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

    conf = config.Config("gensim_sentence2vec")
    MIDDLE_PATH = conf.PROJECT_PATH + "/middle" 

    def get_filename():
        str = open(MIDDLE_PATH+"/file_index.txt").read()
        filenames = str.split("\n")
        filenames.pop()
        return(filenames)
    
    def sentid2filepath(filenames, sentstr):
        """
        sent_0 から fileのpathを見つける
        query ならNoneを返す
    
        @param: "sent_0" (string)
        """
        m = re.search('^sent_(.*)$', sentstr)
        # # sent is not match
        # if m:
        #     exit("sentid is not match")
        p = filenames[int(m.group(1))]
        if p == "query":
            return None
        else: 
            return p

    # vocabを求める
    # sents_str = ht.file_read(MIDDLE_PATH+"/corpus.txt").replace(' ', '')
    # sents = sents_str.split("\n")
    # ht.pp("vocab; %s" % str(len(ht.TextCollection(sents).vocab([]))))

    # データの設定
    labelsentences = LabeledLineSentence("%s/corpus.txt" % MIDDLE_PATH, "sent")
    sentences = labelsentences.sentences()

    # モデル作成
    # model = Doc2Vec(sentences, size=100, window=8, min_count=5, workers=4)
    model = Doc2Vec(alpha=0.025, min_alpha=0.025, workers=4)  # use fixed learning rate
    model.build_vocab(sentences)
     
    for epoch in range(20):
        model.train(sentences)
        model.alpha -= 0.002  # decrease the learning rate
        model.min_alpha = model.alpha  # fix the learning rate, no decay

    # fileのpathを取得するため
    filenames = get_filename()

    # sent 0 ~ 36 is query
    for i in range(37):
        q_sentid = "sent_"+str(i)

        # 似ているドキュメントを出力
        similaries = model.most_similar(q_sentid, topn=len(model.syn0))
        sim_list = [(label, sim) for label, sim in similaries if re.search('sent', label)]

        f = open(conf.RESULT_PATH+"/"+str(i+1).zfill(2)+".txt", "w")

        count = 0
        for (sentid, sim) in sim_list: 
            p = sentid2filepath(filenames, sentid)

            # this is query
            if p is None: 
                continue

            f.write(p+" "+str(sim)+"\n")

            # 上位1000個を取得
            if count >= 999:
                break

            count += 1

        f.close()


