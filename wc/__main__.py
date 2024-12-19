import argparse
from os.path import exists, isdir
from sys import argv

def main():
    parser = argparse.ArgumentParser(description="Print  newline,  word, and byte counts for each FILE, and a total line if more than one FILE is specified. A word is a non-zero-length sequence of printable characters delimited by white space.")

    # add arguments
    parser.add_argument("FILE", type=str, nargs="*", help="With no FILE, or when FILE is -, read standard input.")
    parser.add_argument("-v", "--version", action="store_true", help="output version information and exit.")

    # parse arguments
    args = parser.parse_args()

    # version details
    if args.version:
        print("v0.1.0")
        print("Based on the tool written by Paul Rubin and David MacKenzie.")
        quit(0)

    if len(args.FILE) > 0:
        for path in args.FILE:
            # check file validity
            if not exists(path):
                print(f"{argv[0]}: {path}: No such file or directory")
                continue
            if isdir(path):
                print(f"{argv[0]}: {path}: Is a directory")
                continue

if __name__ == "__main__":
    main()
