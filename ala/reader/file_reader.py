import os
import sys
import time

currentdir = os.path.dirname(__file__)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from config import Configuration


def read_logs_file(parser, log_file_name='apache_logs1'):
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    relative_file_path = '../../data/' + log_file_name

    abs_file_path = os.path.join(script_dir, relative_file_path)

    start = time.time()

    with open(abs_file_path, "r") as f:
        Configuration.ALAprint('Opened logs file!', 1)
        for line in f:
            parser.parseLine(line)
        Configuration.ALAprint('Finished parsing lines', 1)

    Configuration.ALAprint('Preprocessing parsed logs', 1)
    parser.preprocess()

    end = time.time()
    Configuration.ALAprint(f"Finished. Reading and processing took: {end-start}s", 2)


