import lib
import logging
import argparse
from pathlib import Path
from csfile import CsFile, File

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--generate-all", dest="generall",
                       action="store_true", help="Generate .sha1 for source")
    group.add_argument("-n", "--generate-new", dest="genernew",
                       action="store_true", help="Generate .sha1 for new files. Default")
    parser.add_argument("-c", "--clear", action="store_true", help="Clear .sha1 orphans")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode, no output")
    parser.add_argument("-l", type=str, dest="log", metavar=" LOG", help="Write output to log file")
    args = parser.parse_args()

    if args.log:
        try:
            logging.basicConfig(filename=args.log, filemode='a', format='%(asctime)s %(message)s',
                                datefmt='%d.%m.%Y %H:%M:%S', level=logging.DEBUG)
        except PermissionError:
            print("Can't write to log file, permission error")
            args.log = False

    B = 100 * (2 ** 20)  # buffer_size
    Q = args.quiet
    L = args.log

    if not args.generall:
        args.genernew = True

    if args.log:
        logging.debug("-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-")
        logging.debug(f"args.source={args.source}")
        logging.debug(f"args.quiet={args.quiet}")

    news = []
    orphans = []
    if Path(args.source).exists():
        sha1_file = CsFile.get_instance(args.source)
        source_list = [file for file in lib.file_array(sha1_file, real_file=True)]
        sha1_list = [file for file in lib.file_array(sha1_file, real_file=False)]
        orphans = sorted(list(set(sha1_list) - set(source_list)))
        news = sorted(list(set(source_list) - set(sha1_list)))
    else:
        lib.print_out("No such source folder.", Q, L)
        raise SystemExit(0)

    if args.clear:
        if orphans:
            lib.print_out("", Q, L)
            msg = "Cleaning .sha1 orphans"
            sha1_file.delete_sha1(orphans, msg, Q, L)

    def regen_sha1(names_array):
        lib.print_out("", Q, L)
        checksums = []
        for x in names_array:
            checksums.append(File(x, lib.sha1_write(args.source, x, B, Q, L)))
        sha1_file.add_sha1(checksums)

    if args.generall:
        regen_sha1(source_list)

    if args.genernew:
        regen_sha1(news)

    sha1_file.write_file()
