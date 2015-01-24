#!ruby
# -*- coding: utf-8 -*-

module NTCIR
    # 
    # delete_slide
    #   文字数が少ないスライド，一貫性の低いスライドを取り除く
    #   
    #   slide_list: 検索対象のファイルリスト
    #   pmi_hash: 2単語間のPMI値を格納した二重ハッシュ
    #   acceptance_rate: 受理率．どれだけのスライドを検索に使用するか．[0-1]で指定
    #   
    #   checked_slide_list: 不要なスライドを取り除いた，検索対象のファイルリスト
    #
    def self.delete_slide(slide_list, pmi_hash, acceptance_rate=1.0)
        min_char = 100
        
        checked_slide_list = []

        # 文字数によるスクリーニング
        slide_list.each { |slide_path| 
            content = File::open(slide_path).read
            
            if content.length <= min_char
                next
            end

            coherency = calc_coherency(content, pmi_hash)
            checked_slide_list.push([ slide_path, coherency ])
        }

        # 一貫性によるスクリーニング
        number_of_accept = (checked_slide_list.length * acceptance_rate).to_int  # 受理するスライドの枚数

        checked_slide_list.sort! { |a,b| b[1]<=>a[1] }
        # arr.slice!(n, n-1)で，arrは何も変わらない
        checked_slide_list.slice!( (number_of_accept)..(checked_slide_list.length-1) )
        checked_slide_list.map!{|elem| elem[0]}
        
        return checked_slide_list
    end

    # 
    # calc_coherency
    #   文章の一貫性を[1,-1]で計算する．
    #
    #   sentence:文章．
    #   pmi_hash:2単語のPMI値を格納した二重ハッシュ
    #
    #   coherency:文章の一貫性
    #
    def self.calc_coherency(sentence, pmi_hash)
        coherency = 0.0
        
        noun_list = getWordList(sentence, "sentence")\
                    .select{|elem| elem[1] == "名詞"}\
                    .map{|elem| elem[0]}

        combination_arr = noun_list.combination(2)\
                               .to_a\
                               .collect{|elem| elem.sort}\
                               .uniq

        combination_arr.each { |combination| 
            word1 = combination[0]
            word2 = combination[1]

            coherency += pmi_hash[word1][word2]
        }

        coherency /= combination_arr.length.to_f

        return coherency
    end

    # 
    # get_sumpmi
    #   文章中の単語のsumPMI値を計算する．
    #
    #   sentence:文章．
    #   pmi_hash:2単語のPMI値を格納した二重ハッシュ
    #
    #   sum_pmi:文章中の単語のsumPMI値を格納したハッシュ
    #
    def self.get_sumPMI(sentence, pmi_hash)
        sum_pmi = Hash::new(0)
            
        noun_list = getWordList(sentence, "sentence")\
                   .select{|elem| elem[1] == "名詞"}\
                   .map{|elem| elem[0]}

        combination_arr = noun_list.combination(2)\
                                   .to_a\
                                   .collect{|elem| elem.sort}\
                                   .uniq

        combination_arr.each { |combination| 
            word_interest = combination[0]
            word_other = combination[1]

            # puts "#{word_interest}\t#{word_other}\t#{pmi_hash[word_interest][word_other]}"
            sum_pmi[word_interest] += pmi_hash[word_interest][word_other]
            sum_pmi[word_other] += pmi_hash[word_interest][word_other]
        }

        return sum_pmi
    end

    # 
    # calc_ap
    #   クエリに対しての平均適合率(Average Precision)を計算する．
    #
    #   result:検索結果．スライド番号を要素とし，順位の降順に並べたArray
    #   answer:正解．スライド番号を要素とし，順位の降順に並べたArray
    #
    #   ap:平均適合率
    #
    def self.calc_ap(result, answer)
        numerator = 1.0       # 分子
        denominator = 1.0     # 分母
        ap = 0

        result.each { |slide_number| 
            index = answer.index(slide_number)
            if index != nil
                ap += (numerator / denominator)
                numerator += 1
            end

            denominator += 1
        }

        ap /= answer.length.to_f

        return ap
    end

    def self.read_all_file(file_list)
        result_str = ""
        file_list.each { |file_path| 
            result_str += File::open(file_path).read
            result_str += "\n"
        }
        
        return result_str
    end

end
