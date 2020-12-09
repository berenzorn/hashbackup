import os
import lib
import shutil
import logging
import argparse
from pathlib import Path


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
            logging.basicConfig(filename=args.log, filemode='a', format='%(asctime)s %(message)s',
                                datefmt='%m.%d.%Y %H:%M:%S', level=logging.DEBUG)
        except PermissionError:
            print("Can't write to log file, permission error")
            args.log = False

    buffer_size = 1024**2 * 100

    if not args.sync:
        args.append = True

    if args.log:
        logging.debug("-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-")
        logging.debug(f"source={args.source}, destination={args.destination}")
        logging.debug(f"append={args.append}, sync={args.sync}")
        logging.debug(f"delete={args.delete}, quiet={args.quiet}")

    if(Path(args.source).exists()) and (Path(args.destination).exists()):
        # 0 - files in src and dst, 1 - new in src, 2 - not in src
        source_list = lib.new_files(args.source, args.destination)
    else:
        lib.print_out("No such source or destination folder.", args.quiet, args.log)
        raise SystemExit(0)

    if source_list[1]:
        lib.print_out("", args.quiet, args.log)
        lib.print_out("New files in source: ", args.quiet, args.log)
        for i in source_list[1]:
            lib.print_out(f"{i}", args.quiet, args.log)

    for_copy = []
    if args.delete:
        if source_list[2]:
            lib.print_out("", args.quiet, args.log)
            lib.print_out("Files not in source: ", args.quiet, args.log)
            for x in source_list[2]:
                lib.print_out(f"{x}", args.quiet, args.log)
            lib.print_out("", args.quiet, args.log)
            lib.print_out("Removing these files", args.quiet, args.log)
            for x in source_list[2]:
                try:
                    os.remove(Path(f"{args.destination}\\{x}"))
                    os.remove(Path(f"{args.destination}\\{x}.sha1"))
                except FileNotFoundError:
                    pass
                except PermissionError:
                    pass
    if args.sync:
        for_copy += lib.exist_files_check(args.source, args.destination, source_list[0],
                                          buffer_size, args.quiet, args.log)
    if source_list[1]:
        for x in source_list[1]:
            for_copy.append(x)

    if for_copy:
        lib.print_out("", args.quiet, args.log)
        for x in for_copy:
            try:
                lib.print_out(f"Copying file {x}", args.quiet, args.log)
                shutil.copy(f"{args.source}\\{x}", args.destination)
                shutil.copy(f"{args.source}\\{x}.sha1", args.destination)
            except FileNotFoundError:
                lib.sha1_write_queue(args.source, x, buffer_size, args.quiet, args.log)
                shutil.copy(f"{args.source}\\{x}.sha1", args.destination)
