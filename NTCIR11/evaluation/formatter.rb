#!ruby
# -*- coding: utf-8 -*-

# require File.expand_path('../../rubyLib/vital', __FILE__)
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

#================================================================================
#
#================================================================================

def getRootFormat(run_formatstr, system_formatstr, result_formatstr)
    root_formatstr = 
"<ROOT>
    %s
    %s
    %s
</ROOT>"

    result_str = sprintf(root_formatstr, run_formatstr, system_formatstr, result_formatstr)
    return result_str
end


# 
# priority           : 1
# transcription      : REF-WORD-MATCH
# query_transcription: REF-WORD-MATCH
#
def getRunFormat(priority, transcription, query_transcription)
run_formatstr = 
    "<RUN>
        <SUBTASK>SQ-SCR</SUBTASK>
        <SYSTEM-ID>HYM14</SYSTEM-ID>
        <UNIT>SLIDE-GROUP</UNIT>
        <PRIORITY>%d</PRIORITY>
        <TRANSCRIPTION>%s</TRANSCRIPTION>
        <QUERY-TRANSCRIPTION>%s</QUERY-TRANSCRIPTION>
    </RUN>"
    sprintf(run_formatstr, priority, transcription, query_transcription)
end

# 
# machine_spec: Intel(R) Core(TM)i7 CPU X980 3.33GHz, memory:24GHz
# offline_time: 00:00:10
#
def getSystemFormat(machine_spec, offline_time)
system_formatstr = 
    "<SYSTEM>
        <OFFLINE-MACHINE-SPEC>
            %s
        </OFFLINE-MACHINE-SPEC>
        <OFFLINE-TIME>
            %s
        </OFFLINE-TIME>
    </SYSTEM>"

    sprintf(system_formatstr,machine_spec, offline_time)
end

def getResultFormat(result_file_arr)
    format_start = "\t\t<QUERY id=\"SpokenQueryDoc-SQSCR-formal-%04d\">\n"
    format_end = "\t\t</QUERY>\n"
    candidate_format = "\t\t\t<CANDIDATE rank=\"%s\" lecture=\"%s\" slide=\"%s\" />\n"

    format_str = "<RESULT>\n"

    for i in 0..result_file_arr.length-1
        file_path = result_file_arr[i]
        p file_path


        file = File::open(file_path)\
                    .read\
                    .split("\n")


        format_str += sprintf(format_start, i+1)
        
        max_rank = 1000
        if (file.size < max_rank)
            max_rank = file.size
        end
        
        for rank in 0..(max_rank-1) #999
            file_name = file[rank].match(/(\d+\-\d+_\d+)/)[1]
            # matchdata$B7?$+$iJ8;zNs$K(B
            lecture = file_name.match(/^\d+\-\d+/).to_s
            # slide = file_name.match(/\d+$/).to_s.to_i.to_s
            slide = ((file_name.match(/\d+$/).to_s.to_i) + 1).to_s
            
            candidate_str = sprintf(candidate_format, (rank+1).to_s, lecture, slide)
            format_str += candidate_str
        end
        format_str += format_end
    end

    format_str += "\t</RESULT>"

    return format_str
end

# ============================================================

# ========== $B@_DjItJ,(B ==========

# 引数: projectのresult path
if ARGV[0] == nil and ARGV[1] == nil
  abort "args error (NOTE: result path set to args)"
end

sdr_result_dir = ARGV[0]
run_id = ARGV[1]

require 'fileutils'
if !FileTest.exist?(File.expand_path( "../#{run_id}", __FILE__))
    FileUtils.mkdir(File.expand_path( "../#{run_id}", __FILE__))
end

out_name = File.expand_path("../#{run_id}/result.txt", __FILE__)

priority = 1
doc_transcription= "MANUAL"
query_transcription = "MANUAL"
# doc_transcription= "REF-WORD-MATCH"
# query_transcription = "REF-WORD-MATCH"
machine_spec = "Intel(R) Core(TM)i7 CPU X980 3.33GHz, memory:24GHz"
offline_time = "0:15:58"

# ========== end of $B@_DjItJ,(B ==========

file_list = getFileList(sdr_result_dir)
run_formatstr = getRunFormat(priority, doc_transcription, query_transcription)
system_formatstr = getSystemFormat(machine_spec, offline_time)
result_formatstr = getResultFormat(file_list)

out_f = File::open(out_name, "w")
out_f.puts getRootFormat(run_formatstr, system_formatstr, result_formatstr)
