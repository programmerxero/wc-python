import argparse
from os.path import exists, isdir
from sys import argv

PROGRAM_NAME = argv[0]

def hex_escape(s):
    from string import ascii_letters, digits, punctuation
    printable = ascii_letters + digits + punctuation + " "
    return "".join([x if x in printable else r"\x{0:02x}".format(ord(x)) for x in s])

def get_path_from_file(path):
    file_list = []
    if not exists(path):
        print(f"{PROGRAM_NAME}: cannot open '{path}' for reading: No such file or directory")
    elif isdir(path):
        print(f"{PROGRAM_NAME}: {path}: read error: Is a directory")
    with open(path, "r") as file:
        data = file.read()
        curr_path = ""
        for char in data:
            if char == "\0":
                if len(curr_path) > 0: # not empty
                    file_list.append(curr_path)
                curr_path = ""
                continue
            curr_path += char
        if len(curr_path) > 0:
            file_list.append(curr_path)
    return file_list

def get_file_details(path):
    from os.path import getsize
    details = {"bytes": getsize(path),
               "chars": 0,
               "lines": 0,
               "max_line_length": 0,
               "words": 0,}
    with open(path, "r") as file:
        line_length = 0
        is_in_word = False
        for char in file.read():
            if char.isspace():
                if is_in_word:
                    details["words"] += 1
                    is_in_word = False
            else:
                is_in_word = True
            details["chars"] += 1
            if char == "\n":
                details["lines"] += 1
                if line_length > details["max_line_length"]:
                    details["max_line_length"] = line_length
                line_length = 0
                continue
            line_length += 1
        if line_length > details["max_line_length"]:
            details["max_line_length"] = line_length
        if is_in_word:
            details["words"] += 1
            
    return details

def get_stdin_details():
    from sys import stdin
    details = {"bytes": 0,
               "chars": 0,
               "lines": 0,
               "max_line_length": 0,
               "words": 0,}
    try:
        data = stdin.read()
    except KeyboardInterrupt:
        return None
    line_length = 0
    is_in_word = False
    for char in data:
        if char.isspace():
            if is_in_word:
                details["words"] += 1
                is_in_word = False
        else:
            is_in_word = True
        details["bytes"] += len(char.encode("utf-8"))
        details["chars"] += 1
        if char == "\n":
            details["lines"] += 1
            if line_length > details["max_line_length"]:
                details["max_line_length"] = line_length
            line_length = 0
            continue
        line_length += 1
    if line_length > details["max_line_length"]:
        details["max_line_length"] = line_length
    if is_in_word:
        details["words"] += 1
    return details


def report(state, details, path, sep=" "):
    if state & 1:
        print(f"{details['lines']:3}", end=sep)
    if state & 2:
        print(f"{details['words']:3}", end=sep)
    if state & 4:
        print(f"{details['chars']:3}", end=sep) 
    if state & 8:
        print(f"{details['bytes']:3}", end=sep)
    if state & 16:
        print(f"{details['max_line_length']}", end=sep)
    print(path)

def get_state(args):
    # 1 for lines
    # 2 for words
    # 4 for chars
    # 8 for bytes
    # 16 for max line length
    explicit =  0 | int(args.lines) | int(args.words) * 2 | int(args.chars) * 4 | int(args.bytes) * 8 | int(args.max_line_length) * 16
    return explicit if explicit > 0 else 7 # default behavior

def main():
    parser = argparse.ArgumentParser(description="Print  newline,  word, and byte counts for each FILE, and a total line if more than one FILE is specified. A word is a non-zero-length sequence of printable characters delimited by white space.")

    # add arguments
    parser.add_argument("FILE", type=str, nargs="*", help="With no FILE, or when FILE is -, read standard input.")
    parser.add_argument("-v", "--version", action="store_true", help="output version information and exit.")
    parser.add_argument("-c", "--bytes", action="store_true", help="print the byte counts")
    parser.add_argument("-m", "--chars", action="store_true", help="print the character counts")
    parser.add_argument("-l", "--lines", action="store_true", help="print the newline counts")
    parser.add_argument("-L", "--max-line-length", action="store_true", help="print the maximum display width")
    parser.add_argument("-w", "--words", action="store_true", help="print the word counts")
    parser.add_argument("--files0-from", type=str, help="read input from the files specified by NUL-terminated names in file F; If F is - then read names from standard input")
    parser.add_argument("--total", type=str, help="when to print a line with total counts; WHEN can be: auto, always, only, never")
    # parse arguments
    args = parser.parse_args()

    # version details
    if args.version:
        print("v1.0.0")
        print("Based on the tool written by Paul Rubin and David MacKenzie.")
        quit(0)
    # total options
    total_values = ["auto", "always", "only", "never"]
    if args.total and args.total not in total_values:
        print(f"{PROGRAM_NAME}: invalid argument ‘{args.total}’ for ‘--total’")
        print("Valid arguments are:")
        for v in total_values:
            print(f" - ‘{v}’")
        print(f"Try '{PROGRAM_NAME} --help' for more information.")
        quit(0)

    files = args.FILE # extract FILE

    program_state = get_state(args) # program state

    # get path from file
    if args.files0_from is not None:
        if len(files) > 0:
            print("file operands cannot be combined with --files0-from")
            print(f"Try '{PROGRAM_NAME} --help' for more information.")
            quit(0)
        files = get_path_from_file(args.files0_from)
    
    # no file
    if len(files) == 0:
        details = get_stdin_details()
        if details:
            report(program_state, details, "", sep="\t")
        quit(0)
    
    # total details
    total_details = {"bytes": 0,
                    "chars": 0,
                    "lines": 0,
                    "max_line_length": 0,
                    "words": 0,}

    # with FILE
    if len(files) > 0:
        details = {}
        for path in files:
            if path == "-":
                details = get_stdin_details()
                if details is None:
                    quit(0) 
                else:
                    if args.total != "only":
                        report(program_state, details, path)
                # add to total
                for k, v in details.items():
                    if k == "max_line_length":
                        total_details[k] = max(total_details[k], v)
                    else:
                        total_details[k] += v
                    details = {}
                continue
            # check file validity
            if not exists(path):
                print(f"{PROGRAM_NAME}: {hex_escape(path)}: No such file or directory")
                continue
            if isdir(path):
                print(f"{PROGRAM_NAME}: {hex_escape(path)}: Is a directory")
                continue
            details = get_file_details(path)
            if args.total != "only":
                report(program_state, details, path)
            # add to total
            for k, v in details.items():
                if k == "max_line_length":
                    total_details[k] = max(total_details[k], v)
                else:
                    total_details[k] += v
            details = {}

        # report total
        if args.total == "only":
            report(program_state, total_details, "")
        if args.total != "never" and (len(files) > 1 or args.total == "always"):
            report(program_state, total_details, "total")
        
if __name__ == "__main__":
    main()
