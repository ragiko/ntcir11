#!/usr/bin/ruby
# -*- coding: utf-8 -*-

require "MeCab"
#====================================================================================================
#    フレーム化された文章を表すクラス
#    【フィールド変数】
#    @sentence        :フレーム化された文章．String型．
#    @content_word    :フレーム化された文章中の内容語．String型を要素とするArray型
#    @confidence        :フレーム信頼度
#    【メンバー関数】
#    getSentence                    :フィールド変数@sentenceを返す
#    getContentWord              :フィールド変数@content_wordを返す
#    countContentWord            :フレーム中の内容語の出現回数を，内容語をキーとしたハッシュで返す．
#    countContentWordCombination :フレーム中の内容語2つの組み合わせの出現回数を，内容語をキーとした二次元ハッシュで返す．
#    calcConfidence                :フレーム中の内容語全ペアから計算されるPMIの平均値を計算する．
#====================================================================================================

class Frame

    #TODO:リファレンスの作成

    def initialize(sentence, content_word, word_score=[])
        #TODO:バリデーション
        @sentence = sentence
        @content_word = content_word
        @word_score = word_score
        # @content_address_list = content_address_list
        @confidence_by_pmi = 0
        @confidence_by_wordscore = 0
    end

    def getSentence
        return @sentence
    end

    def getContentWord
        return @content_word
    end

    def getWordScore
        return @word_score
    end

    def getConfidenceByPMI
        return @confidence_by_pmi
    end

    def logarithmWordScore
        @word_score.collect!{|x|Math::log10(x)}
    end

    def getConfidenceByWordScore
        return @confidence_by_wordscore
    end

    def countContentWord
        word_count = Hash.new{|hash,key| hash[key] = 0}

        @content_word.uniq.each{|word| word_count[word] += 1}    
        #@content_word.each{|word| word_count[word] += 1}        #this may be wrong. 
        return word_count
    end

    #NOTE:content_word_combination[key1][key2] ≠ content_word_combination[key2][key1]
    def countContentWordCombination
        combination_count = Hash.new{|hash_parent,key1| hash_parent[key1] = Hash.new{|hash_child,key2| hash_child[key2] = 0}}

        #collect:[key1,key2]と[key2,key1]の違いに対応するため
        #uniq   :１フレームに電話2回,携帯1回出現したとき，[携帯,電話]のカウント数を1回とするため
        content_word_combination = @content_word.combination(2)\
                                                .to_a\
                                                .collect{|combination| combination.sort}\
                                                .uniq                                    

        content_word_combination.each{|combination| combination_count[combination[0]][combination[1]] += 1}

        return combination_count
    end
    
    #NOTE:この関数はまだ，１フレームに電話2回,携帯1回出現したときに共起回数1回とする処理を入れていない
    def countContentWordCombinationWithWeight
        combination_count = Hash.new{|hash_parent,key1| hash_parent[key1] = Hash.new{|hash_child,key2| hash_child[key2] = 0}}

        #collect:[key1,key2]と[key2,key1]の違いに対応するため
        content_word_combination = @content_word.each_with_index\
                                                .to_a\
                                                .combination(2)\
                                                .to_a\
                                                .collect{|combination| combination.sort{|a,b|a[0]<=>b[0]}}

        content_word_combination.each{|combination|
            combination_count[combination[0][0]][combination[1][0]] += (2 - 0.1*(combination[0][1] - combination[1][1]).abs)
        }

        return combination_count
    end

    def calcConfidenceByPMI(pmi_hash)
        #declaring and initializing sum_pmi : summation of PMI value of this frame.
        sum_pmi = 0
        n_plus = 0

        #calc sum_pmi : add pmi calculated by each pair of words in same frame
        content_combination = @content_word.combination(2).to_a.collect{|combination| combination.sort}    #同じ単語が複数回出ても，そのまま計算する
        content_combination.each {|combination|
            sum_pmi += pmi_hash[combination[0]][combination[1]]
            n_plus += 1
        }
        #confidence is average of PMI.
        n_content_word = @content_word.length
        if n_content_word == 0 || n_content_word == 1
            @confidence_by_pmi = 0.0
        else
            @confidence_by_pmi = sum_pmi / ((n_content_word * (n_content_word-1))/2).to_f
        end

        return @confidence_by_pmi
    end

    def calcConfidenceByWordScore
        sum_score = 0
        @word_score.each {|score|
            sum_score += score.to_f
        }   
        @confidence_by_wordscore = sum_score / @word_score.length.to_f
    end

    #======================================================================
    #   フレーム中の各単語をキーとして，AvgPMIを要素としたハッシュ
    #======================================================================
    
    def getContentWordPMIHash(pmi_hash)
        word_pmi = Hash::new

        for i in 0..(@content_word.length)-1    #content_word[i]: interested_word
            sum_pmi = 0
            for j in 0..(@content_word.length)-1
                if i != j                    #don't calculate PMI(w_i,w_i)
                    sum_pmi += pmi_hash[@content_word[i]][@content_word[j]]
                end
            end
            sum_pmi = sum_pmi.to_f / ((@content_word.length)-1).to_f
            word_pmi[@content_word[i]] = sum_pmi
        end

        return word_pmi
    end
end

# #====================================================================================================
# #    
# #====================================================================================================
# class ASRFrame < Frame
#     def initialize(sentence="", content_word=[])
#         #TODO:バリデーション
#         super(sentence, content_word)
#         @confidence = 0
#     end
# 
#     def getConfidence
#         return @confidence
#     end
# 
#     def calcConfidence(pmi_hash)
#         #declaring and initializing sum_pmi : summation of PMI value of this frame.
#         sum_pmi = 0
#         n_plus = 0
# 
#         #calc sum_pmi : add pmi calculated by each pair of words in same frame
#         content_combination = @content_word.combination(2).to_a.collect{|combination| combination.sort}    #同じ単語が複数回出ても，そのまま計算する
#         content_combination.each {|combination|
#             sum_pmi += pmi_hash[combination[0]][combination[1]]
#             n_plus += 1
#         }
#         #confidence is average of PMI.
#         n_content_word = @content_word.length
#         @confidence = sum_pmi / ((n_content_word * (n_content_word-1))/2).to_f
# 
#     end
# 
#     #======================================================================
#     #   フレーム中の各単語をキーとして，AvgPMIを要素としたハッシュ
#     #======================================================================
#     def getContentWordPMIHash(pmi_hash)
#         word_pmi = Hash::new
# 
#         for i in 0..(@content_word.length)-1    #@content_word[i]: interested_word
#             sum_pmi = 0
#             for j in 0..(@content_word.length)-1
#                 if i != j                    #don't calculate PMI(w_i,w_i)
#                     sum_pmi += pmi_hash[@content_word[i]][@content_word[j]]
#                 end
#             end
#             sum_pmi = sum_pmi.to_f / ((@content_word.length)-1).to_f
#             word_pmi[@content_word[i]] = sum_pmi
#         end
# 
#         return word_pmi
#     end
# 
#     #NOTE:content_word_combination[key1][key2] ≠ content_word_combination[key2][key1]
#     def countContentWordCombination
#         combination_count = Hash.new{|hash_parent,key1| hash_parent[key1] = Hash.new{|hash_child,key2| hash_child[key2] = 0}}
# 
#         #collect:[key1,key2]と[key2,key1]の違いに対応するため
#         #uniq   :１フレームに電話2回,携帯1回出現したとき，[携帯,電話]のカウント数を1回とするため
#         content_word_combination = @content_word.combination(2)\
#                                                 .to_a\
#                                                 .collect{|combination| combination.sort}\
#                                                 .uniq                                    
# 
#         content_word_combination.each{|combination| combination_count[combination[0]][combination[1]] += 1}
# 
#         return combination_count
#     end
#     
#     #NOTE:この関数はまだ，１フレームに電話2回,携帯1回出現したときに共起回数1回とする処理を入れていない
#     def countContentWordCombinationWithWeight
#         combination_count = Hash.new{|hash_parent,key1| hash_parent[key1] = Hash.new{|hash_child,key2| hash_child[key2] = 0}}
# 
#         #collect:[key1,key2]と[key2,key1]の違いに対応するため
#         content_word_combination = @content_word.each_with_index\
#                                                 .to_a\
#                                                 .combination(2)\
#                                                 .to_a\
#                                                 .collect{|combination| combination.sort{|a,b|a[0]<=>b[0]}}
# 
#         content_word_combination.each{|combination|
#             combination_count[combination[0][0]][combination[1][0]] += (2 - 0.1*(combination[0][1] - combination[1][1]).abs)
#         }
# 
#         return combination_count
#     end
# end

#====================================================================================================
#    【概要】
#    文章を名詞の数を基準に，フレームに分割する．
#    【引数】
#    srt                :フレーム化する文章 or ファイル名
#    kind            :it determines that "str" is file_path or sentence.
#    frame_size        :number型．1フレームあたりの名詞の数
#    frame_shift        :number型．フレーム間の名詞の数
#    【戻り値】
#    framed_sentence    :フレーム化された文章の配列．
#====================================================================================================

def getFrameSet(word_pos_list, frame_size, frame_shift, word_confidence_list = [])

    #単語リストと，内容語番地リストの作成
    word_list            = word_pos_list.collect{|word| word[0]}                                                        #collect morpheme only
#     content_word_list      = word_pos_list.select{|word| word[1] == "名詞"}.collect{|noun| noun[0]}                       #collect noun only
#     content_address_list = word_pos_list.each_with_index.select{|word| word[0][1] == "名詞"}.collect{|noun| noun[1]}    #collect index of noun
    content_word_list      = word_pos_list.select{|word| word[1] == "名詞" || word[1] == "動詞"}\
                                          .collect{|noun| noun[0]}                                                      #collect noun and verb
    content_address_list = word_pos_list.each_with_index.select{|word| word[0][1] == "名詞" || word[0][1] == "動詞"}\
                                                        .collect{|noun| noun[1]}                                        #collect index of content word
    
    #>>>>>>>>>>文章のフレーム化<<<<<<<<<<
    n_frame     = 0  #フレーム数．フレーム開始，末尾位置の更新に用いる．
    frame_start = 0  #フレーム開始番地
    frame       = [] #フレーム化した文章の格納用配列

    # フレームサイズやフレームシフトが，word_pos_listより長い場合は，フレーム化せずに形式的にFrameクラスとして返す．
    if frame_size > (word_pos_list.length)
        frame_size = word_pos_list.length
    end

    if frame_size < frame_shift
        frame_shift = frame_size
    end
    
    puts frame_start + frame_size-1
    puts content_address_list.length

    #フレーム末尾位置の更新．フレーム末尾位置が内容語リストの末尾以降にあるまで．
    while((frame_end = frame_start + frame_size-1) < content_address_list.length)
        #フレーム作成
        #framed_sentence.push(word_list.slice(content_address_list[frame_start], content_address_list[frame_end]).join())
        
        framed_sentence = word_list[content_address_list[frame_start]..content_address_list[frame_end]]
        content_word = content_word_list[frame_start..frame_end]
        framed_confidence = []
        if word_confidence_list != []
            framed_confidence = word_confidence_list[content_address_list[frame_start]..content_address_list[frame_end]]
        end
        # framed_content_address_list = content_address_list[frame_start..frame_end]
        frame.push(Frame.new(framed_sentence, content_word, framed_confidence))

        #フレーム数とフレーム開始位置の再設定
        n_frame += 1
        frame_start = n_frame * frame_shift
    end

    # 末端部分のフレーム化
#     framed_sentence = word_list[content_address_list[frame_start]..content_address_list[(content_address_list.length - 1)]]
#     content_word = content_word_list[frame_start..(content_word_list.length - 1)]
    framed_sentence = word_list[content_address_list[frame_start]..content_address_list[(content_address_list.length - 1)]]
    content_word = content_word_list[frame_start..(content_word_list.length - 1)]
    framed_confidence = []
    if word_confidence_list != []
        framed_confidence = word_confidence_list[content_address_list[frame_start]..content_address_list[(content_address_list.length - 1)]]
    end
    # framed_content_address_list = content_address_list[frame_start..frame_end]
    frame.push(Frame.new(framed_sentence, content_word, framed_confidence))

    return frame

end

#====================================================================================================
#   Frameクラスに統合されました．その為不要．    
#====================================================================================================
# class ASRFrame < Frame
#     def initialize(sentence="", content_word=[])
#         #TODO:バリデーション
#         super(sentence, content_word)
#         @confidence = 0
#     end
# 
#     def getConfidence
#         return @confidence
#     end
# 
#     def calcConfidence(pmi_hash)
#         #declaring and initializing sum_pmi : summation of PMI value of this frame.
#         sum_pmi = 0
#         n_plus = 0
# 
#         #calc sum_pmi : add pmi calculated by each pair of words in same frame
#         content_combination = @content_word.combination(2).to_a.collect{|combination| combination.sort}    #同じ単語が複数回出ても，そのまま計算する
#         content_combination.each {|combination|
#             sum_pmi += pmi_hash[combination[0]][combination[1]]
#             n_plus += 1
#         }
#         #confidence is average of PMI.
#         n_content_word = @content_word.length
#         @confidence = sum_pmi / ((n_content_word * (n_content_word-1))/2).to_f
# 
#     end
# 
#     #======================================================================
#     #    単語をキーとし，PMI平均値を格納したハッシュを返す
#     #======================================================================
# 
# #    def calcWordAvgPMI(pmi_hash)
# #        sum_pmi = 0
# #        
# #        for i in 0..@content_word.length-1
# #            if i != address
# #                word_combination = [@content_word[i], @content_word[address]]
# #                word_combination.sort!
# #                #puts word_combination[0] + "\t" + word_combination[1] + "\t" + pmi_hash[word_combination[0]][word_combination[1]].to_s
# #                sum_pmi += pmi_hash[word_combination[0]][word_combination[1]]
# #            end
# #        end
# #
# #        sum_pmi = sum_pmi.to_f / (((@content_word.length)-1).to_f)
# #        puts @content_word[address] + " -> " + sum_pmi.to_s
# #        return sum_pmi
# #    end
#     
#     def getContentWordPMIHash(pmi_hash)
#         word_pmi = Hash::new
# 
#         for i in 0..(@content_word.length)-1    #@content_word[i]: interested_word
#             sum_pmi = 0
#             for j in 0..(@content_word.length)-1
#                 if i != j                    #don't calculate PMI(w_i,w_i)
#                     sum_pmi += pmi_hash[@content_word[i]][@content_word[j]]
#                 end
#             end
#             sum_pmi = sum_pmi.to_f / ((@content_word.length)-1).to_f
#             word_pmi[@content_word[i]] = sum_pmi
#         end
# 
#         return word_pmi
#     end
# end

#====================================================================================================
#    【概要】
#    文章を名詞の数を基準に，フレームに分割する．
#    【引数】
#    srt                :フレーム化する文章 or ファイル名
#    kind            :it determines that "str" is file_path or sentence.
#    frame_size        :number型．1フレームあたりの名詞の数
#    frame_shift        :number型．フレーム間の名詞の数
#    【戻り値】
#    framed_sentence    :フレーム化された文章の配列．
#====================================================================================================

# 単語信頼度をフレームに追加していないversion
# def getFrameSet(word_pos_list, frame_size, frame_shift)
# 
#     #単語リストと，内容語番地リストの作成
#     word_list            = word_pos_list.collect{|word| word[0]}                                                        #collect morpheme only
#     content_word_list      = word_pos_list.select{|word| word[1] == "名詞"}.collect{|noun| noun[0]}                       #collect noun only
#     content_address_list = word_pos_list.each_with_index.select{|word| word[0][1] == "名詞"}.collect{|noun| noun[1]}    #collect index of noun
#     
#     #>>>>>>>>>>文章のフレーム化<<<<<<<<<<
#     n_frame     = 0  #フレーム数．フレーム開始，末尾位置の更新に用いる．
#     frame_start = 0  #フレーム開始番地
#     frame       = [] #フレーム化した文章の格納用配列
#     
#     #フレーム末尾位置の更新．フレーム末尾位置が内容語リストの末尾以降にあるまで．
#     while((frame_end = frame_start + frame_size-1) < content_address_list.length)
#         #フレーム作成
#         #framed_sentence.push(word_list.slice(content_address_list[frame_start], content_address_list[frame_end]).join())
#         
#         framed_sentence = word_list[content_address_list[frame_start]..content_address_list[frame_end]].join(" ")
#         content_word = content_word_list[frame_start..frame_end]
#         frame.push(Frame.new(framed_sentence, content_word))
# 
#         #フレーム数とフレーム開始位置の再設定
#         n_frame += 1
#         frame_start = n_frame * frame_shift
#     end
#     
#     #余った文章もフレーム化
#     framed_sentence = word_list[content_address_list[frame_start]..content_address_list[content_address_list.length-1]].join(" ")
#     content_word = content_word_list[frame_start..(content_word_list.length-1)]
#     frame.push(Frame.new(framed_sentence, content_word))
# 
#     return frame
# 
# end

# #====================================================================================================
# #    [abstract]
# #    same as "getFrameSet" except that this function returns not Frame class but ASRFrame class
# #====================================================================================================
# def getASRFrameSet(word_pos_list, frame_size, frame_shift)
# 
#     #単語リストと，内容語番地リストの作成
#     word_list            = word_pos_list.collect{|word| word[0]}                                                        #collect morpheme only
#     content_word_list      = word_pos_list.select{|word| word[1] == "名詞"}.collect{|noun| noun[0]}                       #collect noun only
#     content_address_list = word_pos_list.each_with_index.select{|word| word[0][1] == "名詞"}.collect{|noun| noun[1]}    #collect index of noun
#     
#     #>>>>>>>>>>文章のフレーム化<<<<<<<<<<
#     n_frame     = 0  #フレーム数．フレーム開始，末尾位置の更新に用いる．
#     frame_start = 0  #フレーム開始番地
#     frame       = [] #フレーム化した文章の格納用配列
#     
#     #フレーム末尾位置の更新．フレーム末尾位置が内容語リストの末尾以降にあるまで．
#     while((frame_end = frame_start + frame_size-1) < content_address_list.length)
#         #フレーム作成
#         #framed_sentence.push(word_list.slice(content_address_list[frame_start], content_address_list[frame_end]).join())
#         
#         framed_sentence = word_list[content_address_list[frame_start]..content_address_list[frame_end]].join(" ")
#         content_word = content_word_list[frame_start..frame_end]
#         frame.push(ASRFrame.new(framed_sentence, content_word))
# 
#         #フレーム数とフレーム開始位置の再設定
#         n_frame += 1
#         frame_start = n_frame * frame_shift
#     end
# 
#     return frame
# 
# end

#====================================================================================================
#    【概要】
#    ディレクトリのパスを受け取り，ディレクトリ内のファイル名リストを返す
#    【引数】
#    directory_path    :ディレクトリのパス(絶対パス，相対パスは問わない)
#    【戻り値】
#    file_list        :directory_path中の各ファイルの絶対パス(String型)を要素としたArray型配列
#                     ただし，ディレクトリ名は要素としない．
#====================================================================================================

def getFileList(directory_path, option="absolute")
    absolute_path = File::expand_path(directory_path) + "/"                                        
    file_list = Dir::entries(absolute_path).sort                                                
    file_list.delete_if{|file_name| file_name == "." || file_name == ".."}                      #カレントディレクトリ，ペアレントディレクトリを消す
    file_list.delete_if{|file_name| File::ftype(absolute_path + file_name) == "directory"}      #ディレクトリを消す

    #ファイル名を絶対パスに
    case option
    when "absolute"
        for i in 0..(file_list.length-1)
            file_list[i] = absolute_path + file_list[i]
        end

    #ファイル名を相対パスに
    when "relative"
        for i in 0..(file_list.length-1)
            file_list[i] = directory_path + file_list[i]
        end
    
    #lsと同じ挙動に
    when "listup"
        #do nothing
    else
        puts "getFileList:invalid option! option is"
        puts option
    end
    
    return file_list
end

# 内容重複のため，コメントアウト
# #====================================================================================================
# #    【概要】
# #    CSJのXMLから，形態素の品詞リストを返す．
# #    【引数】
# #    xml_path
# #    option
# #    【戻り値】
# #    word_list
# #====================================================================================================
# 
# def getWordListFromXML(sentence, option="")
#     word_list = []
# 
#     sentence.each_line{|line|
#         #単語そのものと，品詞情報を格納する配列
#         word_information = []
# 
#         #XML文中から単語を探す．単語があれば，その単語の読みも探す．
#         if line =~ /PlainOrthographicTranscription="(.*?)"/
#             word = $1                            #if文が入ると$1が消えると思われる
#             if word != "(?"                        #単語が変な文字列でなければ，格納
#                 word_information.push(word)
# 
#                 if line =~ /SUWPOS="(.*?)"/        #単語が見つかったので，読みを探して格納
#                     word_information.push($1)
#                 end
#             end
#         end
#         word_list.push(word_information)        #一つの単語情報を，形態素の品詞リストに加える
#     }
#     #オプション指定時の設定
#     case option
#     when "uniq"
#         word_list.uniq!
#     when ""
# 
#     else
#         print "option " + option + " is not supported."
#         exit 2
#     end
# 
#     return word_list
# end

#====================================================================================================
#    [abstract]
#    get word_part-of-speech list from asrlog.
#    [arguments]
#    
#    [return]
#
#====================================================================================================

def getWordListFromAsrLog(log, noun_hash, option="")
    #open asrlog file.
    # log.gsub!(/\n/, " ")        #delete \n

    #make word_list in asrlog
    # word_list = log.split(/ /)
    word_list = log
    word_pos_list = []

    #convert from asrlog word list to word-pos-list
#     word_list.each{|word|
#         if noun_hash[word] == true
#             word_pos_list.push([word, "名詞"])
#         else
#             word_pos_list.push([word, "other"])
#         end
#     }

    word_list.each{|word|
        if noun_hash[word] == "名詞"
            word_pos_list.push([word, "名詞"])
        elsif noun_hash[word] == "動詞"
            word_pos_list.push([word, "動詞"])
        else
            word_pos_list.push([word, "other"])
        end
    }
    return word_pos_list
end

#====================================================================================================
#    [abstract]
#    morphological analyse the specified documents, then return Word-PartOfSpeech list.
#    [arguments]
#    
#====================================================================================================

def getWordList(arg, kind, option = "")

    #TODO:implement asrlog parser
    word_list = []

    case kind
    #if 1st argument is "file"
    when "file"
        #check 1st argument is XML or not.
        if arg =~ /^.*?\.xml$/
            word_list = getWordListFromXML(arg, option)
        #if 1st argument isn't XML, open the file (then variable "doc" becomes sentence) 
        else
            # puts File::expand_path(arg)
            doc = open(File::expand_path(arg)).read
            word_list = getWordListFromSentence(doc, option)
        end
    
    when "sentence"
        word_list = getWordListFromSentence(arg, option)

    when "asrlog"
        log = arg[0].split(" ")
        word_list = getWordListFromAsrLog(log, arg[1])

    when "asrlog-file"
        #check 1st argument conteins "asrlog file path" and "noun_list hash"
        if arg.length != 2
            puts "invalid arguments!"
        else
            log = open(arg[0]).read
            log = log.gsub(/\n/, " ").split(" ")
            word_list = getWordListFromAsrLog(log, arg[1])
        end

    when "asrlog-frame"
        #check 1st argument conteins "asrlog file path" and "noun_list hash"
        if arg.length != 2
            puts "getWordList::invalid arguments!" + " arg is" 
            p arg
        else
            word_list = getWordListFromAsrLog(arg[0], arg[1])
        end
    
    when ""
        #do nothing
    else
        puts "getWordList::invalid kind!" + " kind is"
        p kind
    end
    
    return word_list
end

#====================================================================================================
#    【概要】
#    文書を形態素解析し，形態素の品詞リストを返す
#    【引数】
#    sentence        :形態素解析する文字列．
#    option            :オプション文字列．現在は uniq のみ
#        "uniq"
#            重複する形態素リストは消す
#
#    【戻り値】
#    word_list    :文書中の全形態素に対して，[形態素,品詞]を要素としたArray型配列
#====================================================================================================

def getWordListFromSentence(sentence, option="")

    #TODO:可変長引数に対応させる．

    #doc = open(File::expand_path(file_path)).read
    word_list = MeCab::Tagger.new("--node-format=%m,%f[0]\\n --eos-format="" ").parse(sentence)
    if word_list == nil 
        return []
    end
    word_list = word_list.split("\n")            #split by WordInformation
    word_list.collect!{|word| word.split(",")}    #split by morpheme and part of speech
    
    #オプション指定時の設定
    case option
    when "uniq"
        word_list.uniq!
    when ""

    else
        print "option " + option + " is not supported."
        exit 2
    end

    return word_list
end


#================================================================================
#    [abstract]
#    Extract "morpheme" and "PartOfSpeech" from xml of CSJ.
#    result is printed by stdout.
#
#    [arguments]
#    xml_path    :specify target's path. it doesn't care whether it is absolute or not.
#    option        :you can get result removing same elements.
#================================================================================

def getWordListFromXML(xml_path, option="")
    xml = open(File::expand_path(xml_path)).read
    word_list = []
    
    xml.each_line{|line|
        morpheme = ""            
        partOfSpeech = ""   
    
        #find part of speech
        if line =~ /SUWPOS="(.*?)"/
            #warning: if PartOfSpeech is overrided.
            if partOfSpeech != ""
                puts "PartOfSpeech is overrided!!!"
            end
            partOfSpeech = $1
        end
    
        #find morpheme
        if line =~ /PlainOrthographicTranscription="(.*?)"/
            #warning: if morpheme is overrided.
            if morpheme != ""
                puts "morpheme is overrided!!!"
            end
            morpheme = $1
        end
    
        #if "morpheme" and "partOfSpeech" is detected, then push them into stack "word_list".
        if (morpheme != "") and (partOfSpeech != "")
            word_list.push([morpheme, partOfSpeech])
        end

    }

    case option
    when "uniq"
        word_list.uniq!
    end

    return word_list
end

#====================================================================================================
#    [abstract]
#    
#====================================================================================================

def mergeHash(hash_array, coefficient_array)
    #validation
    if hash_array.length != coefficient_array.length
        puts "mergeHash: length of the array is not equal!"
    else
        merged_hash = Hash::new{|hash,key|hash[key] = 0}
        n_hash = hash_array.length

        for i in 0..n_hash-1
            #ハッシュ値に係数をかける
            hash_array[i].each {|key, value|
                hash_array[i][key] = coefficient_array[i] * value
            }

            #ハッシュを統合する
            # merged_hash.merge!(hash_array[i])
            merged_hash.merge!(hash_array[i]){|key, a, b| a + b}
        end
    end

    return merged_hash
end

#====================================================================================================
#   【概要】
#   2ベクトル間のコサイン尺度を計算する
#   【引数】
#   vector1
#   vector2 :現在ハッシュのみ対応．デフォルト値0であること，要素が数値であることが要件
#   【戻り値】
#   コサイン尺度(Integer)
#====================================================================================================

def calcCosineScale(vector1, vector2)
    # calc inner product
    inner_product = 0

    word_list = (vector1.keys & vector2.keys)
    word_list.each {|word|
        inner_product += vector1[word] * vector2[word]
    }

    # calc each vector norm
    vector1_norm = 0
    vector2_norm = 0

    vector1.each {|key, value|
        vector1_norm += value * value
    }
    vector1_norm = Math::sqrt(vector1_norm)

    vector2.each {|key, value|
        vector2_norm += value * value
    }
    vector2_norm = Math::sqrt(vector2_norm)
    
    if vector1_norm * vector2_norm == 0
        cos_scale = 0.0
    else
        cos_scale = inner_product / (vector1_norm * vector2_norm)
    end
    

    return cos_scale
end

# 
# PMIによるベクトルの類似度を，基底の向きのみで計算する
# 
# vector1:ハッシュ．キーが単語であるようにすること．
# vector2:ハッシュ．キーが単語であるようにすること．
# pmi_hash:PMI値を格納した二重ハッシュ．
#
# return: 類似度，float．
#
def calcPMISimilarity(vector1, vector2, pmi_hash)
    similarity = 0.0
    wordlist_1 = vector1.keys
    wordlist_2 = vector2.keys
    plus_count = wordlist_1.length * wordlist_2.length
    
    wordlist_1.each { |word1| 
        wordlist_2.each { |word2| 
            if word1 == word2
                similarity += 1
            elsif
                similarity += pmi_hash[word1][word2]
            end
        }
    }

    if plus_count != 0
        similarity /= plus_count.to_f
    end

    return similarity
end

# 
# PMIによるベクトルの類似度を，重み付きで計算する
# 
# vector1:ハッシュ．キーが単語であるようにすること．
# vector2:ハッシュ．キーが単語であるようにすること．
# pmi_hash:PMI値を格納した二重ハッシュ．
#
# return: 類似度，float．
#
def calcPMISimilarityWithWeight(vector1, vector2, pmi_hash)
    similarity = 0.0
    wordlist_1 = vector1.keys
    wordlist_2 = vector2.keys
    
    denominator = 0.0
    wordlist_1.each { |word1| 
        wordlist_2.each { |word2| 
            if word1 == word2
                similarity += vector1[word1] * vector2[word2]
            elsif
                similarity += vector1[word1] * vector2[word2] * pmi_hash[word1][word2]
            end
            denominator += vector1[word1] * vector2[word2]
        }
    }

    if denominator == 0
        return 0.0
    end
    similarity /= denominator

    return similarity
end

# ====================================================================================================
#   Julius認識結果のhypファイルの内容をパース，認識結果の分かち書きをStringで，単語信頼度をArrayで返す
# argument : hyp(string)
# NOTE : 認識結果と信頼度が1:1対応でないと，うまく動かない．
#        search failed した認識結果には，この関数を適応しないこと．
# ====================================================================================================

def parseHyp(hyp)
    # 認識結果は<s> ... <\s> となっている
    # 単語信頼度はcmscore ... となっている
    asr_result = ""
    word_confidence = []

    hyp.each {|line|
        # 認識結果の行の場合
        if line =~ /^<s> (.*?)<\/s>$/
            asr_result += $1
        # 単語信頼度の行の場合
        elsif line =~ /^cmscore \d\.\d{3} (.*?) \d\.\d{3}$/
            confidence_str = $1
            word_confidence.push(confidence_str.split(" "))
        end
    }
    word_confidence.flatten!
    
    return [asr_result, word_confidence]
end

def putsDoubleHash(hash)
    hash.each { |key1,hash_parent| 
        hash_parent.each { |key2, value| 
            puts key1.inspect + "\t" + key2.inspect + "\t" + value.inspect
        }
    }
end
