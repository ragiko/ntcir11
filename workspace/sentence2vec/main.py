#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import hymlab.text as ht
import re
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/sentence2vec_core')
from word2vec import Word2Vec, Sent2Vec, LineSentence

def get_filename():
    str = open(TMP_DIR_PATH+"/file_index.txt").read()
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

if __name__ == '__main__':
    WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
    TMP_DIR_PATH = WORKSPACE_DIR + "/middle" 
    RESULT_DIR_PATH = WORKSPACE_DIR + "/result" 

    # fileのpathを取得するため
    filenames = get_filename()

    model = Word2Vec.load_word2vec_format(TMP_DIR_PATH+"/sent.txt.vec", binary=False)

    # sent 0 ~ 36 is query
    for i in range(37):
        q_sentid = "sent_"+str(i)
        sim_list = model.most_similar([q_sentid], topn=2000)

        f = open(RESULT_DIR_PATH+"/"+str(i+1).zfill(2)+".txt", "w")

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


        



