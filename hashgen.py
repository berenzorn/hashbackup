import os
import hashlib
import argparse
import logging
from pathlib import Path


def file_array(path, real_file):
    if real_file:
        return [file for file in Path(path).iterdir()
                if file.is_file() and not file.name.endswith('.sha1')]
    else:
        return [file for file in Path(path).iterdir()
                if file.is_file() and file.name.endswith('.sha1')]


def hashgen_file(filename, buffsize, quiet, log):
    filehash = hashlib.sha1()
    if not quiet:
        print(f"Generating hash for: {filename}")
    if log:
        logging.debug(f"Generating hash for: {filename}")
    with open(filename, mode='rb') as file:
        while True:
            try:
                buffer = file.read(buffsize)
            except MemoryError:
                print("Not enough memory.")
                logging.error("Not enough memory.")
                raise SystemExit(0)
            filehash.update(buffer)
            if not buffer:
                break
    return filehash.hexdigest()


def sha1_write(path, name, buffer, quiet, log):
    sha1sum = hashgen_file(Path(f"{path}\\{name}"), buffer, quiet, log)
    with open(Path(f"{path}\\{name}.sha1"), 'w', encoding="utf8") as sha1file:
        sha1file.write(f"{sha1sum}   {name}")  # ← 3 spaces!
    return sha1sum


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-g", "--generate", action="store_true", help="Generate .sha1 for source")
    group.add_argument("-c", "--clear", action="store_true", help="Clear .sha1 orphans")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode, no output")
    parser.add_argument("-b", type=int, dest="buffer", metavar=" BUFFER", help="Buffer size in MB", default=100)
    parser.add_argument("-l", type=str, dest="log", metavar=" LOG", help="Write output to log file")
    args = parser.parse_args()

    if args.log:
        logging.basicConfig(filename=args.log, filemode='a', format='%(asctime)s %(message)s',
                            datefmt='%m.%d.%Y %H:%M:%S', level=logging.DEBUG)
    if args.buffer <= 0:
        args.buffer = 1
    buffer_size = args.buffer * 1024**2

    if args.log:
        logging.debug("-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-")
        logging.debug(f"args.source={args.source}")
        logging.debug(f"args.quiet={args.quiet}, args.buffer={args.buffer}")

    orphans = []
    if Path(args.source).exists():
        source_list = [file.name for file in file_array(args.source, True)]
        if args.clear:
            sha1_list = [file.name[:-5] for file in file_array(args.source, False)]
            orphans = sorted(list(set(sha1_list) - set(source_list)))
    else:
        print("No such source folder.")
        if args.log:
            logging.error("No such source folder.")
        raise SystemExit(0)

    if args.clear:
        if not args.quiet:
            print("\nCleaning .sha1 orphans: ")
            for i in orphans:
                print(i)

        if args.log:
            logging.debug("")
            logging.debug("Cleaning .sha1 orphans: ")
            for i in orphans:
                logging.debug(f"{i}")

        for x in orphans:
            try:
                os.remove(Path(f"{args.source}\\{x}.sha1"))
            except FileNotFoundError:
                pass

    if args.generate:
        if not args.quiet:
            print("\nFiles in source: ")
            for i in source_list:
                print(i)

        if args.log:
            logging.debug("")
            logging.debug("Files in source:")
            for i in source_list:
                logging.debug(f"{i}")

        if not args.quiet:
            print()
        if args.log:
            logging.debug("")
        for x in source_list:
            try:
                os.remove(Path(f"{args.source}\\{x}.sha1"))
            except FileNotFoundError:
                pass
            sha1_write(args.source, x, buffer_size, args.quiet, args.log)
