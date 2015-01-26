require 'systemu'

WORKSPACE_RESULT_PATH = './workspace/result'
WORKSPACE_TMP_PATH = './workspace/tmp'
FORMAT_RESULT_PATH = './NTCIR11/evaluation/result.txt'
MAP_JAR_PATH = './NTCIR11/evaluation/evalsqscr.jar'

def systemu_msg sh
  status, stdout, stderr = systemu sh
  res = {
      out: stdout,
      error: stderr,
      msg: [ '$Run shell: '+sh, '$Error: '+stderr ].join("\n")+"\n"
  }
end

task :init do
  FileUtils.mkdir('./workspace/tmp') if !FileTest.exist?('./workspace/tmp')
  FileUtils.mkdir('./workspace/result') if !FileTest.exist?('./workspace/result')
end

task :main do
  # 実行
  exe = 'python ./workspace/main.py'
  puts systemu_msg(exe)[:msg]
end

task :format do
  # 中間ファイル作成
  if Dir.glob(WORKSPACE_RESULT_PATH+'/*').size == 0
    puts "ERROR: workspace results is not exist"
    exit
  end
  format = 'ruby ./NTCIR11/evaluation/formatter.rb'
  puts systemu_msg(format)[:msg]
end

task :map do
  # 結果の表示
  if !FileTest.exist?(FORMAT_RESULT_PATH)
    puts "ERROR: format result file is not found"
    exit
  end
  Dir.chdir("./NTCIR11/evaluation/") do
    map = "java -jar ./evalsqscr.jar ./result.txt"
    puts systemu_msg(map)[:msg]
    puts systemu_msg(map)[:out]
  end
end

task :all => [:clean, :main, :format, :map]
task :clean => [:clean_result, :clean_format, :clean_tmp]

task :clean_result do
    # main.pyの実行結果を削除
    FileUtils.rm(Dir.glob(WORKSPACE_RESULT_PATH+'/*'))
end

task :clean_format do
  FileUtils.rm(FORMAT_RESULT_PATH) if FileTest.exist?(FORMAT_RESULT_PATH)
end

task :clean_tmp do
  # tmpファイルを削除
  FileUtils.rm(Dir.glob(WORKSPACE_TMP_PATH+'/*'))
end
