import os
import sys
import time

currentdir = os.path.dirname(__file__)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from ALparser.ALParser import ApacheLogParser


def read_logs_file(parser, log_file_name='apache_logs1'):
    ALparser = parser

    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    relative_file_path = '../../data/' + log_file_name

    abs_file_path = os.path.join(script_dir, relative_file_path)

    start = time.time()

    with open(abs_file_path, "r") as f:
        print('Opened logs file!')
        for line in f:
            ALparser.parseLine(line)
        print('Finished parsing lines')

    print('Preprocessing parsed logs')
    ALparser.preprocess()

    end = time.time()
    print(f"Finished. Reading and processing took: {end-start}s")


