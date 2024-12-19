import argparse
from os.path import exists, isdir
from sys import argv

def get_file_details(path):
    from os.path import getsize
    details = {'bytes': getsize(path),}
    return details

def report(state, details, path):
    if state & 1:
        print(f"{details['bytes']:3}", end=" ")
    print(path)

def get_state(args):
    # 1 for bytes
    return 0 | int(args.bytes)

def main():
    parser = argparse.ArgumentParser(description="Print  newline,  word, and byte counts for each FILE, and a total line if more than one FILE is specified. A word is a non-zero-length sequence of printable characters delimited by white space.")

    # add arguments
    parser.add_argument("FILE", type=str, nargs="*", help="With no FILE, or when FILE is -, read standard input.")
    parser.add_argument("-v", "--version", action="store_true", help="output version information and exit.")
    parser.add_argument("-c", "--bytes", action="store_true", help="print the byte counts")

    # parse arguments
    args = parser.parse_args()

    # version details
    if args.version:
        print("v0.2.0")
        print("Based on the tool written by Paul Rubin and David MacKenzie.")
        quit(0)
    
    program_state = get_state(args)

    if len(args.FILE) > 0:
        for path in args.FILE:
            # check file validity
            if not exists(path):
                print(f"{argv[0]}: {path}: No such file or directory")
                continue
            if isdir(path):
                print(f"{argv[0]}: {path}: Is a directory")
                continue
            report(program_state, get_file_details(path), path)

if __name__ == "__main__":
    main()
