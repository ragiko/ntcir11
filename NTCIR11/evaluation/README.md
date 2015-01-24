How to run
==========
### 評価できるようにXMLの形に整える
formatter.rbの以下の二行を書き換える.  
sdr_result_dir = "result/keyword2vec_web600_nounverb/"  # 入力:検索結果のディレクトリ  
out_name = "./formal/keyword2vec_web600_nounverb.txt"   # 出力:ファイル名  

sdr_result_dirのサンプルは，result_spk/以下のような形式になっていればよい．
  
formatter.rbを実行(Ruby1.9以上)  
$ ruby formatter.rb  
注意:kitanaisia/rubyLibが必要．場所は../rubyLib/

### 評価する
java -jar evalsqscr.jar ./formal/keyword2vec_web600_nounverb.txt
