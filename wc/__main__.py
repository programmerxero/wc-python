import argparse
from os.path import exists, isdir
from sys import argv

def get_path_from_file(path):
    file_list = []
    if not exists(path):
        print(f"{argv[0]}: cannot open '{path}' for reading: No such file or directory")
    elif isdir(path):
        print(f"{argv[0]}: {path}: read error: Is a directory")
    with open(path, "r") as file:
        for line in file:
            start = 0
            for i in range(len(line)):
                if line[i] == "\0" or line[i] == "\n" or i == len(line) - 1: # null seperated values
                    tmp = line[start:i]
                    start = i + 1
                    if len(tmp) > 0: # check valid length
                        file_list.append(tmp)
                    if line[i] == "\0":
                        break
    return file_list

def get_file_details(path):
    from os.path import getsize
    details = {"bytes": getsize(path),
               "chars": 0,
               "lines": 0,
               "max_line_length": 0,}
    with open(path, "r") as file:
        line_length = 0
        for char in file.read():
            details["chars"] += 1
            if char == "\n":
                details["lines"] += 1
                if line_length > details["max_line_length"]:
                    details["max_line_length"] = line_length
                line_length = 0
                continue
            line_length += 1
            
    return details

def get_stdin_details():
    from sys import stdin
    data = stdin.read()
    details = {"bytes": 0,
               "chars": 0,
               "lines": 0,
               "max_line_length": 0}
    line_length = 0
    for char in data:
        details["bytes"] += len(char.encode("utf-8"))
        details["chars"] += 1
        if char == "\n":
            details["lines"] += 1
            if line_length > details["max_line_length"]:
                details["max_line_length"] = line_length
            line_length = 0
            continue
    return details


def report(state, details, path, sep=" "):
    if state & 1:
        print(f"{details['lines']:3}", end=sep)
    if state & 2:
        print(f"{details['chars']:3}", end=sep) 
    if state & 4:
        print(f"{details['bytes']:3}", end=sep)
    if state & 8:
        print(f"{details['max_line_length']}", end=sep)
    print(path)

def get_state(args):
    # 1 for lines
    # 2 for chars
    # 4 for bytes
    # 8 for max line length
    return 0 | int(args.lines) | int(args.chars) * 2 | int(args.bytes) * 4 | int(args.max_line_length) * 8

def main():
    parser = argparse.ArgumentParser(description="Print  newline,  word, and byte counts for each FILE, and a total line if more than one FILE is specified. A word is a non-zero-length sequence of printable characters delimited by white space.")

    # add arguments
    parser.add_argument("FILE", type=str, nargs="*", help="With no FILE, or when FILE is -, read standard input.")
    parser.add_argument("-v", "--version", action="store_true", help="output version information and exit.")
    parser.add_argument("-c", "--bytes", action="store_true", help="print the byte counts")
    parser.add_argument("-m", "--chars", action="store_true", help="print the character counts")
    parser.add_argument("-l", "--lines", action="store_true", help="print the newline counts")
    parser.add_argument("-L", "--max-line-length", action="store_true", help="print the maximum display width")
    parser.add_argument("--files0-from", type=str, help="read input from the files specified by NUL-terminated names in file F; If F is - then read names from standard input")
    # parse arguments
    args = parser.parse_args()

    # version details
    if args.version:
        print("v0.3.0")
        print("Based on the tool written by Paul Rubin and David MacKenzie.")
        quit(0)
    
    files = args.FILE # extract FILE

    program_state = get_state(args) # program state

    # get path from file
    if args.files0_from is not None:
        if len(files) > 0:
            print("file operands cannot be combined with --files0-from")
            print(f"Try '{argv[0]} --help' for more information.")
            quit(0)
        files = get_path_from_file(args.files0_from)
    
    # no file
    if len(files) == 0:
        report(program_state, get_stdin_details(), "", sep="\t")
        quit(0)
    
    # with FILE
    if len(files) > 0:
        for path in files:
            if path == "-":
                report(program_state, get_stdin_details(), path)
                continue
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
