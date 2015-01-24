#!/usr/bin/ruby
# -*- coding: utf-8 -*-

# ロードミスのエラー連発のため，一時的にコメントアウト
# require "vital"

#====================================================================================================
#	【概要】
#	PMI計算時に使用する f(x,y):フレームに単語xと単語yが共起する確率 を計算する．
#	【引数】
#	directory_path	:生起確率学習用のコーパスが存在するディレクトリへのパス．相対パス，絶対パスは問わない．
#	【戻り値】
#	combination_freq		:内容語をキーとし，単語共起確率を値にもつハッシュ．
#====================================================================================================

def learnWordCoOccurrenceProbabilities(directory_path, frame_size, frame_shift, use_weight=false)

	word_freq = Hash.new{|hash,key| hash[key] = 0}
	combination_freq = Hash.new{|hash_parent,key1| hash_parent[key1] = Hash.new{|hash_child, key2| hash_child[key2] = 0}}
	n_frame = 0

	getFileList(directory_path).each{|file_name|
		word_list = getWordList(file_name, "file")
		frame_set = getFrameSet(word_list, frame_size, frame_shift)
		n_frame += frame_set.length
		frame_set.each{|frame|
		#getFrameSet(file_name, "file", frame_size, frame_shift).each{|frame|
			#単語生起回数カウント
			word_freq.merge!(frame.countContentWord){|key,value1,value2| value1 + value2}

			#単語共起回数カウント
            if use_weight
                combination_freq.merge!(frame.countContentWordCombinationWithWeight){|key,hash1,hash2| 
                    hash1.merge(hash2){|key,value1,value2| value1 + value2}
                }
            else
                combination_freq.merge!(frame.countContentWordCombination){|key,hash1,hash2| 
                    hash1.merge(hash2){|key,value1,value2| value1 + value2}
                }
            end
		}
	}
	#チューリング推定量計算
	#no_occur = (word_freq.length * (word_freq.length-1)) / 2	#生起回数0の単語ペア数 = (全単語ペア数) - (キーの存在する単語ペア数)
	no_occur = (word_freq.length * (word_freq.length+1)) / 2	#コンビネーションを重複を許してカウントする．
	occur_once = 0                                              #生起回数1の単語ペア数


	combination_freq.each{|key1, hash|
		no_occur -= hash.length									#値が0より大きいもののみがhashに入る
		occur_once += hash.select{|key,freq| freq == 1}.length
	}

	#combination_freq.default = occur_once.to_f / no_occur.to_f	#共起数0のペアは，チューリング推定量の値を代わりに入れる．
	combination_freq.each{|key1,hash|
		hash.each{|key2,value|
			hash.default = occur_once.to_f / no_occur.to_f			#共起数0のペアは，チューリング推定量の値を代わりに入れる．
		}
	}

	#return combination_freq
	return [word_freq, combination_freq, n_frame]
end

#====================================================================================================
#	【概要】
#	t値を計算する
#	【引数】
#====================================================================================================

def calcTValue(freq_x, freq_y, freq_xy, n_frame)
	return (freq_xy - (( freq_x * freq_y ).to_f/( n_frame ).to_f)).abs.to_f / (Math::sqrt(freq_xy)).to_f
end

#====================================================================================================
#	【概要】
#	単語生起回数および，チューリング推定量によって補正された単語共起回数をもとに，平滑化PMIを計算する．
#	【引数】
#	
#	【戻り値】
#
#====================================================================================================

def learnPMI(word_freq, combination_freq, n_frame, threshold)
	pmi = Hash.new{|hash_parent,key1| hash_parent[key1] = Hash.new{|hash_child, key2| hash_child[key2] = 0}}

	combination_freq.each{|key1,hash|
		hash.each{|key2,value|
			#T値計算
			t_value = calcTValue(word_freq[key1], word_freq[key2], combination_freq[key1][key2], n_frame)

			#T値が閾値より大きいなら，PMIは非零の値を取る
			if t_value > threshold
				pmi[key1][key2] = Math::log((combination_freq[key1][key2] * n_frame).to_f / (word_freq[key1] * word_freq[key2]).to_f)
			end
		}
	}
	return pmi
end

#====================================================================================================
#	[abstract]
#	make PMI hash from text file.
#====================================================================================================

def makePMIHash(pmi_file_path)
	doc = open(pmi_file_path).read
	# pmi_hash = Hash.new{|hash_parent,key1| hash_parent[key1] = Hash.new{|hash_child,key2| hash_child[key2] = 0}}
    pmi_hash = Hash.new { |h, k| h[k] = Hash.new(0) }
	
	doc.lines {|line|
		#declare
		word1 = ""
		word2 = ""
		pmi = 0

		#find "word combination" and "PMI" from "pmi_file"
        # 関谷先輩の形式に合わせるため，一時的に\t から " "とした．
		if line =~ /^(.*?)\t(.*?)\t(.*?)$/
			word1 = $1
			word2 = $2
			pmi = $3.to_f
			pmi_hash[word1][word2] = pmi
			pmi_hash[word2][word1] = pmi	#pmi[word1][word2] = pmi[word2][word1]
		else
			puts "makePMIHash : parse error."
		end
	}

	return pmi_hash
end
