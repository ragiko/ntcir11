#!/usr/bin/env python
# -*- coding: utf-8 -*-

# n-Gram Language Model with Knerser-Ney Smoother
# This code is available under the MIT License.
# (c)2013 Nakatani Shuyo / Cybozu Labs Inc.

import sys, codecs, re, numpy
import json
import nkf
import re

import simplejson as json
import copy

def pp(obj):
    if isinstance(obj, list) or isinstance(obj, dict):
        orig = json.dumps(obj, indent=4)
        print eval("u'''%s'''" % orig).encode('utf-8')
    else:
        print obj

### util ###
# ファイルを読み込み，文字コード変換
def file_read(file_path):
    # スライド番号の抜き出し
    r = re.compile("\d+-\d+_\d+")
    m = r.search(file_path)
    slide_id =  m.group(0)

    # ファイルオープン
    contents = open(file_path).read()
    contents = nkf.nkf("-w -d", contents) \
        .decode("utf_8")
    words = contents.strip().split()
    return {"id": slide_id, "words": words}
### util ###

def cp(obj):
    return list([obj])[0]

class NGram(dict):
    def __init__(self, N, depth=1):
        self.freq = 0
        self.N = N
        self.depth = depth
    def inc(self, v):
        if self.depth <= self.N:
            if v not in self:
                self[v] = NGram(self.N, self.depth + 1)
            self[v].freq += 1
            return self[v]
    def dump(self):
        if self.depth <= self.N:
            return "%d:{%s}" % (self.freq, ",".join("'%s':%s" % (k,d.dump()) for k,d in self.iteritems()))
        return "%d" % self.freq

    def probKN(self, D, given=""):
        assert D >= 0.0 and D <= 1.0
        if given == "":
            voca = self.keys()
            n = float(self.freq)
            return voca, [self[v].freq / n for v in voca]
        else:
            if len(given) >= self.N:
                given = given[-(self.N-1):]
            voca, low_prob = self.probKN(D, given[1:])
            cur_ngram = self
            for v in given:
                if v not in cur_ngram: return voca, low_prob
                cur_ngram = cur_ngram[v]
            g = 0.0 # for normalization
            freq = []
            for v in voca:
                c = cur_ngram[v].freq if v in cur_ngram else 0
                if c > D:
                    g += D
                    c -= D
                freq.append(c)
            n = float(cur_ngram.freq)
            return voca, [(c + g * lp) / n for c, lp in zip(freq, low_prob)]

class Generator(object):
    def __init__(self, ngram):
        self.ngram = ngram
        self.start()
    def start(self):
        self.pointers = []
    def inc(self, v):
        pointers = self.pointers + [self.ngram]
        self.pointers = [d.inc(v) for d in pointers if d != None]
        self.ngram.freq += 1

def main():
    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-n", dest="ngram", type="int", help="n-gram", default=3)
    parser.add_option("-d", dest="discount", type="float", help="discount parameter of Knerser-Ney", default=0.5)
    parser.add_option("-i", dest="numgen", type="int", help="number of texts to generate", default=5)
    parser.add_option("-e", dest="encode", help="character code of input file(s)", default='utf-8')
    parser.add_option("-o", dest="output", help="output filename", default="generated.txt")
    parser.add_option("--seed", dest="seed", type="int", help="random seed")
    (opt, args) = parser.parse_args()

    numpy.random.seed(opt.seed)

    START = u"\u0001"
    END = u"\u0002"

    ws = [
        u'ちょっと',
        u'一',
        u'発表',
        u'者',
        u'ちょっと',
        u'まずい',
        u'か',
        u'も',
        u'しれ',
        u'ませ',
        u'ん',
        u'が',
        u'で',
        u'始め',
        u'たい',
        u'と',
        u'思い',
        u'ます']

    #slide = file_read('/admin/git/chainer-char-rnn/kaldi_space_data/07-01/07-01_011kaldi.txt')

    ngram = NGram(opt.ngram)
    gen = Generator(ngram)
    
    gen2 = copy.deepcopy(gen)

    gen.start()
    words = ws # slide['words']
    wn = len(words)
    for (i, w) in enumerate(words):
        print str(i) + "/" + str(wn)
        gen.inc(w)
    
    print gen.ngram.freq
    print gen2.ngram.freq
    
    del gen2

    # D = opt.discount
    # pp(u'ちょっと')
    # voca, prob = ngram.probKN(D, u'ちょっと')
    # pp(voca)
    # pp(prob)
    #
    # pp(u'ちょっと')
    # voca, prob = ngram.probKN(D, u'ちょっと')
    # pp(voca)
    # pp(prob)
    
    # print ws
    # for (i, w) in enumerate(ws):
    #     voca, prob = ngram.probKN(D, w)
    #     pp(voca)
    #     if i+1 >= len(ws): break
    #     prew = ws[i+1]
    #     try:
    #         id = voca.index(prew)
    #         p = prob[id]
    #     except:
    #         p = 0.0
    #     print prew
    #     print p

if __name__ == "__main__":
    main()
