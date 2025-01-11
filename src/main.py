import argparse

from master import replicate
from slave import receive

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('mode')
    args = parser.parse_args()



    if args.mode == 'master':
        replicate()
    if args.mode == 'slave':
        receive()