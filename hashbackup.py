import os
import lib
import shutil
import logging
import argparse
from pathlib import Path

from csfile import CsFile, File

if __name__ == '__main__':
    """
    1 - append mode.
    New files that are not in the destination - put into copy list.
    2 - sync mode.
    New files that are not in the destination - put into copy list.
    Modified files in the source compared to the destination - put into copy list.
    Files in the destination without hash - put file in the source into copy list.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=str)
    parser.add_argument("destination", type=str)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--append", action="store_true", help="Copy new files only. Default")
    group.add_argument("-s", "--sync", action="store_true", help="Copy new and changed files")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete old files in destination")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    parser.add_argument("-l", type=str, dest="log", metavar=" LOG", help="Write output to log file")
    args = parser.parse_args()

    if args.log:
        try:
            logging.basicConfig(filename=str(args.log), filemode='a', format='%(asctime)s %(message)s',
                                datefmt='%d.%m.%Y %H:%M:%S', level=logging.DEBUG)
        except PermissionError:
            print("Can't write to log file, permission error")
            args.log = False

    B = int(1e6)  # buffer_size
    Q = args.quiet
    L = args.log

    if not args.sync:
        args.append = True

    if args.log:
        logging.debug("-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-")
        logging.debug(f"source={args.source}, destination={args.destination}")
        logging.debug(f"append={args.append}, sync={args.sync}")
        logging.debug(f"delete={args.delete}, quiet={args.quiet}")

    if (Path(args.source).exists()) and (Path(args.destination).exists()):
        src_sha1 = CsFile.get_instance(args.source)
        dst_sha1 = CsFile.get_instance(args.destination)
        # 0 - files in src and dst, 1 - new in src, 2 - not in src
        source_list = lib.new_files(src_sha1, dst_sha1)
    else:
        lib.print_out("No such source or destination folder.", Q, L)
        raise SystemExit(0)

    if source_list[1]:
        lib.print_out("", Q, L)
        lib.print_out("New files in source: ", Q, L)
        for i in source_list[1]:
            lib.print_out(f"{i}", Q, L)

    for_copy = []
    if args.delete:
        if source_list[2]:
            lib.print_out("", Q, L)
            lib.print_out("Missing from source: ", Q, L)
            for x in source_list[2]:
                lib.print_out(f"{x}", Q, L)
            lib.print_out("", Q, L)
            lib.print_out("Removing these files", Q, L)
            dst_sha1.delete_sha1(source_list[2], "", Q, L)
            for x in source_list[2]:
                    os.remove(Path(f"{args.destination}\\{x}"))
    if args.sync:
        lib.print_out("", Q, L)
        for_copy += lib.exist_files_check(src_sha1, dst_sha1, source_list[0], B, Q, L)
    for_copy += source_list[1]
    if for_copy:
        if not args.sync:
            lib.print_out("", Q, L)
        checksums = []
        for x in for_copy:
            lib.print_out(f"Copying file {x}", Q, L)
            shutil.copyfile(f"{args.source}\\{x}", f"{args.destination}\\{x}")
            chksum = src_sha1.read_sha1(x)
            if chksum:
                checksums.append(File(x, chksum))
            else:
                missed_chksum = File(x, lib.sha1_write(args.source, x, B, Q, L))
                checksums.append(missed_chksum)
                src_sha1.add_sha1([missed_chksum])
        dst_sha1.add_sha1(checksums)

    src_sha1.write_file()
    dst_sha1.write_file()
