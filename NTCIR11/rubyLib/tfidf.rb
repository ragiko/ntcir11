#!/usr/bin/ruby
# -*- coding: utf-8 -*-

# require "vital"
#====================================================================================================
#    【概要】
#    文書中の単語の正規化TFを，単語をキーとしたハッシュで返す
#    【引数】
#    args        :it is passed to function "getWordList"
#    kind        :it determines args's kind (example "file", "asrlog", "sentence" and so on.)
#    【戻り値】
#    tf            :単語をキーとし，正規化TF値を保存したハッシュ．
#====================================================================================================
def getTF(args, kind)
    tf = Hash.new
    tf.default = 0
    n_noun = 0     #名詞出現回数.TFの正規化に使用．

    getWordList(args, kind).each{|word|
        if word[1] == "名詞"
            tf[word[0]] += 1 
            n_noun += 1
        end
    }

    #正規化TF計算
    tf.each{|word,value|
        tf[word] = value.to_f / n_noun.to_f
    }

    return tf
end

#====================================================================================================
#   legacy function
#    【概要】
#    単語のIDF値を，単語をキーとしたハッシュで返す．
#    【引数】
#    directory_path    :IDFを計算するファイル群が存在するディレクトリへのパス．絶対パス，相対パスは問わない
#    【戻り値】
#    idf                :単語をキーとし，IDF値を保存したハッシュ
#====================================================================================================

#def getIDF(directory_path, noun_hash="")
#    df  = Hash.new
#    df.default = 0
#    idf = Hash.new
#    idf.default = 0
#    n_file = 0        #ドキュメント数．IDFの計算に使用．
#
#    #DF計算
#    getFileList(File::expand_path(directory_path) + "/").each{|file_path|
#        n_file += 1                                            #ドキュメント数カウント
#        
#        if noun_hash == ""
#            getWordList(file_path, "file", "uniq").each{|word|
#                if word[1] == "名詞" then df[word[0]] += 1 end
#            }
#        else
#            getWordList([ file_path, noun_hash ], "asrlog-file", "uniq").each{|word|            
#                if word[1] == "名詞" then df[word[0]] += 1 end
#            }
#        end
#    }
#    
#    #IDF計算
#    df.each{|word, df|
#        idf[word] = Math::log10(1.0 + (n_file / df.to_f))
#    }
#    
#    return idf
#end

#====================================================================================================
#    【概要】
#    単語のIDF値を，単語をキーとしたハッシュで返す．
#    【引数】
#    file_path_list     :ファイルのへの絶対パスを要素としたArray
#    noun_hash          :名詞リスト(optional) これを指定する場合，形態素解析による品詞情報は使われない
#    【戻り値】
#    idf                :単語をキーとし，IDF値を保存したハッシュ
#====================================================================================================
def getIDF(file_path_list, noun_hash="")
    df  = Hash.new
    df.default = 0
    idf = Hash.new
    idf.default = 0
    n_file = 0        #ドキュメント数．IDFの計算に使用．

    #DF計算
    file_path_list.each{|file_path|
        n_file += 1                                            #ドキュメント数カウント
        
        if noun_hash == ""
            getWordList(file_path, "file", "uniq").each{|word|
                if word[1] == "名詞" then df[word[0]] += 1 end
            }
        else
            getWordList([ file_path, noun_hash ], "asrlog-file", "uniq").each{|word|            
                if word[1] == "名詞" then df[word[0]] += 1 end
            }
        end
    }
    
    #IDF計算
    df.each{|word, df|
        idf[word] = Math::log10(1.0 + (n_file / df.to_f))
    }
    
    return idf
end
#====================================================================================================
#    【概要】
#    文書中の単語のTF-iDF値を，単語をキーとしたハッシュで返す．
#    【引数】
#    sentence        :TF-iDFを計算する文章．
#    directory_path    :ドキュメント郡が存在するディレクトリのパス．絶対パス，相対パスは問わない
#    【戻り値】
#    tf-idf            :単語をキーとし，TF-iDFの値を要素とするハッシュ
#====================================================================================================

def getTFIDF(tf, idf)
    tfidf = Hash.new
    tfidf.default = 0


    #TF-iDFの計算
    tf.each_key{|word|
        tfidf[word] = tf[word] * idf[word]
    }

    return tfidf
end
