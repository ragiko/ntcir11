require 'nokogiri'
require 'pp'
require 'erb'


class Doc
  attr_accessor :name, :is_correct
  
  def initialize(name)
    @name = name
    @is_correct = false
  end
  
  def correct?
    @is_correct
  end
end

# クエリごとのランキングを取得
def parse_xml(doc)
  result_docs_list = []
  
  doc.xpath('//QUERY').each do |query|
    id = query.attribute('id').text
    docs = []
    query.xpath('./CANDIDATE').each do |candidate|
      lecture = candidate.attribute('lecture').text
      slide = candidate.attribute('slide').text
      doc = Doc.new(lecture+"-"+slide)
      docs << doc
    end
    result_docs_list << {id => docs}
  end

  result_docs_list
end

# need/の絶対パス
INSPECTOR_PATH = File.expand_path("..", __FILE__)
NEED_PATH = File.expand_path("../need", __FILE__)

# クエリのIDに対応したランキングされた文書を取得
# use: docs(result_list, "SpokenQueryDoc-SQSCR-formal-0001")
# return: docs
def docs(result_list, query_id)
  result_list.each do |id_docs_hash|
    if id_docs_hash.key?(query_id)
      return id_docs_hash[query_id]
    end
  end
  []
end

# result
doc = Nokogiri::XML(File.open("#{NEED_PATH}/result.txt"))
result_list = parse_xml(doc)

# correct
doc = Nokogiri::XML(File.open("#{INSPECTOR_PATH}/correct.xml"))
correct_list = parse_xml(doc)

# 結果の中に正解が含まれた時
# 結果に目印をつける
correct_list.each do |h|
  query_id = h.keys[0]
  correct_docs = h.values[0]

  # 正解の文書名を取得
  correct_doc_name_list = correct_docs.map{ |doc| doc.name }
  
  result_docs = docs(result_list, query_id)
  result_docs.each do |result_doc|
    # 正解文書内に結果の文書が存在するか
    if correct_doc_name_list.include?(result_doc.name)
      result_doc.is_correct = true
    end
  end
end

# jarを走らせた結果
map_result = File.read("#{NEED_PATH}/map_result.txt")

# make html
# render1: result_list
# render2: map_result
html = File.read("#{INSPECTOR_PATH}/tmp.html")
erb = ERB.new(html)
bind_html = erb.result(binding)
File.write("#{INSPECTOR_PATH}/output/a.html", bind_html)

