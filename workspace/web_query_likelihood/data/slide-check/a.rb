require 'fileutils'

dir = "./data/"
sample = "sample.txt"

list =  File.read("./list.txt").split("\n")
list.each do |l|
  FileUtils.mkdir(dir+l)
  FileUtils.cp(sample, dir+l+"/test.txt")
end
