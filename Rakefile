require 'systemu'

WORKSPACE_PATH = './workspace'
WORKSPACE_RESULT_PATH = './workspace/result'
WORKSPACE_TMP_PATH = './workspace/tmp'
EVALUAION_PATH = './NTCIR11/evaluation'
FORMAT_RESULT_PATH = './NTCIR11/evaluation/result.txt'
MAP_RESULT_PATH = './NTCIR11/evaluation/map_result.txt'
MAP_JAR_PATH = './NTCIR11/evaluation/evalsqscr.jar'

def systemu_msg sh
  status, stdout, stderr = systemu sh
  res = {
      out: stdout,
      error: stderr,
      msg: [ '$Run shell: '+sh, '$Error: '+stderr ].join("\n")+"\n"
  }
end

# project パラメータを指定していないと弾く
def project_param_abort
  if !ENV['p'] 
      abort "paramater not found :: rake p=project_name task"
  end
end

def run_id
  if !!ENV['id']
    return ENV['id']
  else
    return "default"
  end
end

#//////////////
# workflow
#//////////////

# 1. projectを作成
# 2. main.pyに結果を格納するコードを作成
# 3. rake p=tfidf all

#///////////////
# task
#///////////////

task :all => [:clean, :main, :format, :map]
# 計算結果をキャッシュしたソースを消さない
task :all_soft => [:clean_result, :clean_format, :main, :format, :map]
task :format_map => [:format, :map] 
task :clean => [:clean_result, :clean_format, :clean_tmp]

task :init do
  project_param_abort()

  # project 作成
  FileUtils.mkdir(WORKSPACE_PATH+'/'+ENV['p']) if !FileTest.exist?(WORKSPACE_PATH+'/'+ENV['p'])

  Dir.glob(WORKSPACE_PATH+'/'+ENV['p']) do |path|
    # main.py 
    FileUtils.cp(path+'/../../template/main.py', path+'/main.py') if !FileTest.exist?(path+'/main.py')
    # tmp/
    FileUtils.mkdir(path+'/tmp') if !FileTest.exist?(path+'/tmp')
    # result/
    FileUtils.mkdir(path+'/result') if !FileTest.exist?(path+'/result')
  end
end

task :main do |t|
  # 実行
  project_param_abort()
  exe = "python #{WORKSPACE_PATH}/#{ENV['p']}/main.py " + run_id
  puts systemu_msg(exe)[:msg]
end

task :format do |t|
  # 中間ファイル作成
  project_param_abort()
  if Dir.glob(WORKSPACE_PATH+"/"+ENV['p']+'/result/'+run_id+'/*').size == 0
    puts "ERROR: workspace results is not exist"
    exit
  end
  project_path = File.expand_path("../#{WORKSPACE_PATH}/#{ENV['p']}/result/"+run_id, __FILE__)
  format = "ruby ./NTCIR11/evaluation/formatter.rb #{project_path} #{run_id}"
  puts systemu_msg(format)[:msg]
end

task :map do
  # 結果の表示
  if !FileTest.exist?("#{EVALUAION_PATH}/#{run_id}/result.txt")
    puts "ERROR: format result file is not found"
    exit
  end
  
  # 結果ファイルの保管フォルダ
  if !FileTest.exist?("./NTCIR11/evaluation/#{run_id}")
    FileUtils.mkdir("./NTCIR11/evaluation/#{run_id}")
  end

  Dir.chdir("./NTCIR11/evaluation/") do
    map = "java -jar ./evalsqscr.jar ./#{run_id}/result.txt"
    m = systemu_msg(map)
    File.write("./#{run_id}/map_result.txt", m[:out])
    puts m[:msg]
    puts m[:out]
  end
end

task :vis do
  # map値の可視化ツール
  if (FileTest.exist?(FORMAT_RESULT_PATH) and FileTest.exist?(MAP_RESULT_PATH))
    inspector_path = "./inspector"
    FileUtils.cp(FORMAT_RESULT_PATH, "#{inspector_path}/need")
    FileUtils.cp(MAP_RESULT_PATH, "#{inspector_path}/need")
    exe = "ruby #{inspector_path}/visible.rb"
    puts systemu_msg(exe)[:msg]
  else
    puts "[error] file is not exist"
  end
end

task :clean_result do |t|
  # main.pyの実行結果を削除
  project_param_abort()
  FileUtils.rm(Dir.glob(WORKSPACE_PATH+"/"+ENV['p']+'/result/'+run_id+'/*'))
end

task :clean_format do 
  if FileTest.exist?("#{EVALUAION_PATH}/#{run_id}/result.txt")
    FileUtils.rm("#{EVALUAION_PATH}/#{run_id}/result.txt")
  end
end

task :clean_tmp do |t|
  # tmpファイルを削除
  project_param_abort()
  FileUtils.rm(Dir.glob(WORKSPACE_PATH+"/"+ENV['p']+'/tmp/*'))
end
