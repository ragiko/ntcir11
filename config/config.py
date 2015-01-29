#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

class Config:
    def __init__(self, project_name):
        self.WORKSPACE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/../workspace"
        self.PROJECT_PATH = self.WORKSPACE_PATH + "/" + project_name

        # spoken data
        self.SPOKEN_QUERY_PATH = self.WORKSPACE_PATH + "/../NTCIR11/Data/formalrun_query/formalrun_query.txt"
        self.SPOKEN_DOC_PATH = self.WORKSPACE_PATH + "/../NTCIR11/Data/slide_asr_noblank"

        # write data
        self.WRITE_QUERY_PATH = self.WORKSPACE_PATH + "/../NTCIR11/Data/formalrun_query/formalrun_query_text.txt"
        self.WRITE_DOC_PATH = self.WORKSPACE_PATH + "/../NTCIR11/Data/slide"
 
        # /tmp and /result
        self.TMP_PATH = self.PROJECT_PATH + "/tmp" 
        self.RESULT_PATH = self.PROJECT_PATH + "/result" 

if __name__ == '__main__':
    conf = Config("bm25")
    print "WORKSPACE_PATH " + str(os.path.exists(conf.WORKSPACE_PATH))
    print "PROJECT_PATH " + str(os.path.exists(conf.PROJECT_PATH))
    print "SPORKEN_QUERY_PATH " + str(os.path.exists(conf.SPORKEN_QUERY_PATH))
    print "SPORKEN_DOC_PATH " + str(os.path.exists(conf.SPORKEN_DOC_PATH))
    print "WRITE_QUERY_PATH " + str(os.path.exists(conf.WRITE_QUERY_PATH))
    print "WRITE_DOC_PATH " + str(os.path.exists(conf.WRITE_DOC_PATH))
    print "TMP_PATH " + str(os.path.exists(conf.TMP_PATH))
    print "RESULT_PATH " + str(os.path.exists(conf.RESULT_PATH))

