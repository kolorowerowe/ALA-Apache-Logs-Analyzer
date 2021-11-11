import os


def read_logs_file():

    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    relative_file_path = '../../data/apache_logs1'

    abs_file_path = os.path.join(script_dir, relative_file_path)

    f = open(abs_file_path, "r")

    print('Opened logs file! First line:')
    print(f.readline())


