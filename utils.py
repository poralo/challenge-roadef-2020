import os
import sys
import numpy as np
import json

# CUR_DIR = os.getcwd()


def read_json(filename: str):
    """Read a json file and return data as a dict object"""

    print('Reading json file ' + filename + '...')
    with open(filename, 'r') as f:
        instance = json.load(f)
    print('Done')

    return instance


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('ERROR: expecting 1 argument: paths to instance')
    else:
        instance_file = sys.argv[1]
        instance = read_json(instance_file)
