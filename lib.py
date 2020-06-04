import os
import queue
import hashlib
import logging
import threading
from pathlib import Path


class Block:

    def __init__(self, number, data):
        self.number = number
        self.data = data


def file_array(path, real_file):
    """
    :return: files list OR .sha1 list in <path> folder
    """
    if real_file:
        return [file for file in Path(path).iterdir()
                if file.is_file() and not file.name.endswith('.sha1')]
    else:
        return [file for file in Path(path).iterdir()
                if file.is_file() and file.name.endswith('.sha1')]


def new_files(src, dst):
    """
    :return: files list that are in both folders,
    files only in source and only in destination
    """
    src_array = file_array(src, True)
    dst_array = file_array(dst, True)
    src_list = [file.name for file in src_array]
    dst_list = [file.name for file in dst_array]
    sd_diff = sorted(list(set(src_list) - set(dst_list)))
    ds_diff = sorted(list(set(dst_list) - set(src_list)))
    # 0 - files in src and dst, 1 - new in src, 2 - not in src
    return dst_list, sd_diff, ds_diff


def exist_files_check(src, dst, file_list, buffer, quiet, log):
    """
    Checking hashes in shared file_list for source and destination.
    :return: files list in source whose hash is different from destination
    OR if file in destination has no hash.
    """
    def dict_mount(path, name, buffer, quiet, log, need_update):
        try:
            with open(Path(f"{path}\\{name}.sha1"), 'r') as s:
                string = s.readline()
        except FileNotFoundError:
            return sha1_write_queue(path, name, buffer, quiet, log) if need_update else 0
        return string.split("   ")[0]  # ← 3 spaces!

    src_dict = {}
    dst_dict = {}
    for file in file_list:
        src_dict[file] = dict_mount(src, file, buffer, quiet, log, True)
        dst_dict[file] = dict_mount(dst, file, buffer, quiet, log, False)

    diff_list = [name for name, sha1 in dst_dict.items() if src_dict[name.rstrip()] != sha1]
    return diff_list


def print_out(msg, quiet, log):
    if not quiet:
        print(f"{msg}")
    if log:
        logging.debug(f"{msg}")


def sha1_write_queue(path, name, bufsize, quiet, log):

    q = queue.Queue()
    hash_array = {}
    block_counter = 0

    def worker():
        while True:
            sha = hashlib.sha1()
            item = q.get()
            sha.update(item.data)
            hash_array[item.number] = sha.digest()
            q.task_done()

    filename = Path(f"{path}\\{name}")
    print_out(f"Generating hash for: {filename}", quiet, log)
    # TODO config param
    threading.Thread(target=worker, daemon=True).start()
    threading.Thread(target=worker, daemon=True).start()
    with open(filename, mode='rb') as file:
        while True:
            try:
                block = Block(block_counter, file.read(bufsize))
            except MemoryError:
                print_out("Not enough memory.", quiet, log)
                raise SystemExit(0)
            if not block.data:
                break
            q.put(block)
            block_counter += 1
    q.join()
    sha1 = hashlib.sha1()
    for i in sorted(list(hash_array)):
        sha1.update(hash_array[i])
    with open(Path(f"{path}\\{name}.sha1"), 'w', encoding="utf8") as sha1file:
        sha1file.write(f"{sha1.hexdigest()}   {name}")  # ← 3 spaces!
    return sha1.hexdigest()


def sha1_remove(source, array, msg, quiet, log):
    print_out(msg, quiet, log)
    for x in array:
        try:
            os.remove(Path(f"{source}\\{x}.sha1"))
        except FileNotFoundError:
            pass
