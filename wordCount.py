#! /usr/bin/env python3

import sys        # command line arguments
import re         # regular expression tools
import os         # checking if file exists
import subprocess # executing program

# set input and output files
if len(sys.argv) is not 3:
    print("Correct usage: wordCount.py <input text file> <output file>")
    exit()

inputFname = sys.argv[1]
outputFname = sys.argv[2]

#make sure text files exist
if not os.path.exists(inputFname):
    print ("text file input %s doesn't exist! Exiting" % inputFname)
    exit()

#master dictionary
master_dict = {}

# attempt to open input file
with open(inputFname, 'r') as inputFile:
    for line in inputFile:
        # get rid of newline characters
        line = line.strip()
        # split line on whitespace and punctuation
        words = re.split('\W+', line)
        for w in words:
            if w:
                master_dict[w.lower()] = 1 if w.lower() not in master_dict.keys() else master_dict[w.lower()] + 1
                    

with open(outputFname, 'w') as outputFile:
    master_keys = sorted(master_dict.keys())
    for key in master_keys:
        outputFile.write(key + ' ' + str(master_dict[key]) + '\n')
