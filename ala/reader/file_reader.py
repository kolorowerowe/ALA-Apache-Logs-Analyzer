import os
import sys

currentdir = os.path.dirname(__file__)
parentdir = os.path.dirname(currentdir)
print(parentdir)
sys.path.insert(0, parentdir)

from ALparser.ALParser import ApacheLogParser


def read_logs_file(log_file_name='apache_logs1'):
    ALparser = ApacheLogParser()

    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    relative_file_path = '../../data/' + log_file_name

    abs_file_path = os.path.join(script_dir, relative_file_path)

    with open(abs_file_path, "r") as f:
        print('Opened logs file!')
        for line in f:
            ALparser.parseLine(line)
        print('Finished parsing lines')

    print('Processing parsed logs')
    ALparser.process()


