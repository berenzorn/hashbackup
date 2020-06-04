import lib
import logging
import argparse
from pathlib import Path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("-g", "--generate", action="store_true", help="Generate .sha1 for source")
    parser.add_argument("-c", "--clear", action="store_true", help="Clear .sha1 orphans")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode, no output")
    parser.add_argument("-l", type=str, dest="log", metavar=" LOG", help="Write output to log file")
    args = parser.parse_args()

    if args.log:
        try:
            logging.basicConfig(filename=args.log, filemode='a', format='%(asctime)s %(message)s',
                                datefmt='%m.%d.%Y %H:%M:%S', level=logging.DEBUG)
        except PermissionError:
            print("Can't write to log file, permission error")
            args.log = False

    buffer_size = 1024**2 * 100

    if not args.clear:
        args.generate = True

    if args.log:
        logging.debug("-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-")
        logging.debug(f"args.source={args.source}")
        logging.debug(f"args.quiet={args.quiet}")

    orphans = []
    if Path(args.source).exists():
        source_list = [file.name for file in lib.file_array(args.source, True)]
        if args.clear:
            sha1_list = [file.name[:-5] for file in lib.file_array(args.source, False)]
            orphans = sorted(list(set(sha1_list) - set(source_list)))
    else:
        lib.print_out("No such source folder.", args.quiet, args.log)
        raise SystemExit(0)

    if args.clear:
        if orphans:
            lib.print_out("", args.quiet, args.log)
            msg = "Cleaning .sha1 orphans"
            lib.sha1_remove(args.source, orphans, msg, args.quiet, args.log)

    if args.generate:
        lib.print_out("", args.quiet, args.log)
        for x in source_list:
            try:
                lib.sha1_write_queue(args.source, x, buffer_size, args.quiet, args.log)
            except PermissionError:
                lib.print_out("IO Error, no permission to read/write", args.quiet, args.log)
