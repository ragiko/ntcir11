#!ruby
# -*- coding: utf-8 -*-

require "./vital"
require "pp"
#================================================================================
#   スライド検索の重みと講演検索の重みを結合するプログラム
#   ruby connect_result.rb 0.8
#================================================================================

# ====================変数設定部====================
lec_coef = ARGV[0]          # 講演の重み，上の例の場合"0.8"
lec_coef = lec_coef.to_f    # string型 -> float型

# 
# 入力・出力ディレクトリ設定部,ディレクトリ構造は以下のような感じ
#
#- result/                         
# |+ Nsimilarity_web1200_noun/     
# |- bm25/                         
#  |  01.txt   # 01.txt ~ 37.txt 1つ1つがparse_slide_resultの引数
#  |  02.txt                       
#  |  03.txt                       
#
#- result_lecture/                   
# |+ Nsimilarity_web1200_noun/       
# |- bm25/                           
#  |  01.txt  # 01.txt ~ 37.txt 1つ1つがparse_lec_resultの引数
#  |  02.txt  
#  |  03.txt  
#
lecture_dir = "./lecture/"
slide_dir = "./slide/"
out_dir = "./result/"

# ====================変数設定部終了====================

# ====================関数宣言部====================
# 
# 講演検索結果の１ファイルから，類似度を読み取る
# @param file_path : 1クエリに対する講演検索結果のファイル(以下のような形式を想定)
#       ./Data/sa.txt/10-13_fix.sa.txt	1.0
#       ./Data/sa.txt/09-02_fix.sa.txt	0.78964814157
#       ./Data/sa.txt/12-10_fix.sa.txt	0.774797936935
#       ./Data/sa.txt/09-06_fix.sa.txt	0.666957219617
# 
# @return result : result["10-13"] = 1.0
#
def parse_lec_result(file_path)
    result = Hash::new(0.0)
    content = File::open(file_path).read\
                                   .split("\n")
    
    content.each {|line|
        if line =~ /(\d+\-\d+)_fix\.sa\.txt\t(.*?)$/ #自分の形式(テキストクエリ)
        # if line =~ /(\d+\-\d+)_fix\.match_word\.jout\t(.*?)$/ #自分の形式
        # if line =~ /(\d+\-\d+)_fix_match_word_jout\.txt.*? (\-.*?)$/   #先輩の形式
            value = $2.to_f
            result[$1] = value
            # result[$1] = Math::exp(value)
        end
    }

    return result
end

# 
# スライド検索結果の１ファイルから，類似度を読み取る
# @param file_path : １クエリに対するスライド検索結果のファイル(以下のような形式を想定)
#       ./Data/slide/09-06_016.txt	1.0
#       ./Data/slide/09-06_007.txt	0.987617091552
#       ./Data/slide/10-13_003.txt	0.954099232098
#       ./Data/slide/13-05_030.txt	0.927464169028
# 
# @return result : result["10-13"]["003"] = 0.954099232098
#
def parse_slide_result(file_path)
    result = Hash::new{|h,k| h[k] = Hash::new(0.0)}
    content = File::open(file_path).read\
                                   .split("\n")
    
    content.each {|line|
        if line =~ /(\d+\-\d+)_(\d+)\.txt(.*?)$/    #自分の形式(テキストクエリ)
        # if line =~ /(\d+\-\d+)_(\d+)_asr\.txt(.*?)$/    #自分の形式
        # if line =~ /(\d+\-\d+)_(\d+)_asr.*?: (\-.*?)$/      #先輩の形式
            value = $3.to_f
            # result[$1][$2] = Math::exp(value)
            result[$1][$2] = value
        end
    }

    return result
end

# 
#
class Similarity
    attr_accessor :file_name
    attr_accessor :similarity

    def initialize
        @file_name = ""
        @simillarity = 0.0
    end

end

# 
# Similarity型の変数出力用関数
# out_fにFile.open("hoge.txt", "w")したオブジェクトを渡すと，
# 標準出力ではなくファイルに結果を出力する
#
def putsSimilariry(sililarity, out_f=nil)
    if out_f == nil
        puts sililarity.file_name + "\t" + sililarity.similarity.inspect
    else
        out_f.puts sililarity.file_name + "\t" + sililarity.similarity.inspect
    end
end

# ====================関数宣言部終了====================

# ====================Main文====================

if !File::exist?(out_dir)
    Dir::mkdir(out_dir)
end
out_dir += lec_coef.to_s + "/"

# 
# p lecture_result_list
#   ["01.txt", "02.txt", "03.txt", ...]
# p slide_result_list 
#   ["01.txt", "02.txt", "03.txt", ...]
#
lecture_result_list = getFileList(lecture_dir, "listup")
slide_result_list = getFileList(slide_dir, "listup")

## 1クエリ毎に，線形結合した類似度を計算し，ソートしてバッファに格納
result_arr = [] # クエリ毎に，ファイル名-類似度 がソートされた結果が格納されるバッファ

lecture_result_list.each { |name| 
    # lecture_result_path   : "./result_lecture/bm25/01.txt" 
    # slide_result_path     : "./result/bm25/01.txt"             
    lecture_result_path = lecture_dir + name    
    slide_result_path = slide_dir + name        

    ## ex)講演番号が"10-13",スライド番号が003の場合,以下のように指定すればよい
    # p lecture_result["10-13"]         # ハッシュ
    # p slide_result["10-13"]["003"]    # 二重ハッシュ
    lecture_result = parse_lec_result(lecture_result_path)
    slide_result = parse_slide_result(slide_result_path)

    # 重み付き線形和を算出する
    connect_result = [] # 1クエリの ファイル名-類似度 格納バッファ
    slide_result.each { |lec_number,h| 
        h.each { |slide_number, v| 
            value = ( lec_coef * lecture_result[lec_number] ) + ( (1-lec_coef) * slide_result[lec_number][slide_number] )

            # ファイル名と類似度を1構造体に格納して，配列にプッシュ
            similarity = Similarity.new
            similarity.file_name = "Data/slide/" + lec_number + "_" + slide_number + ".txt"
            similarity.similarity = value

            connect_result << similarity
        }
    }
    
    # 1クエリの，スコアのソート
    connect_result.sort!{|a,b| b.similarity <=> a.similarity}
    result_arr << connect_result
}

# ファイル保存ステップ
index = 0       
if !File::exist?(out_dir)
    Dir::mkdir(out_dir)
end

result_arr.each { |result| 
    index += 1  # クエリ番号
    out_f = File::open(out_dir + sprintf("%02d", index) + ".txt", "w")
    result.each { |similarity| 
        putsSimilariry(similarity, out_f)
    }
}
