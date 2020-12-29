import os
import queue
import hashlib
import logging
import threading
from pathlib import Path
from csfile import CsFile


def file_array(cs_file: CsFile, real_file: bool):
    """
    :return: files list OR .sha1 list in <path> folder
    """
    if real_file:
        return [file.name for file in Path(cs_file.path).iterdir()
                if file.is_file() and not file.name.endswith('.sha1')]
    else:
        return [file for file in cs_file.array]


def new_files(src_file: CsFile, dst_file: CsFile):
    """
    :return: files list that are in both folders,
    files only in source and only in destination
    """
    src_array = file_array(src_file, real_file=True)
    dst_array = file_array(dst_file, real_file=True)
    src_list = [file for file in src_array]
    dst_list = [file for file in dst_array]
    sd_diff = sorted(list(set(src_list) - set(dst_list)))
    ds_diff = sorted(list(set(dst_list) - set(src_list)))
    common = sorted(list(set(dst_list) & set(src_list)))
#     0 - files in src and dst, 1 - new in src, 2 - not in src
    return common, sd_diff, ds_diff


def dict_mount(path, name, checksums, buffer, quiet, log, need_update: bool):
    if name in checksums.keys():
        return checksums[name], False
    else:
        return (sha1_write(path, name, buffer, quiet, log), True) if need_update else (0, False)


def exist_files_check(src_sha1, dst_sha1, file_list, buffer, quiet, log):
    """
    Checking hashes in shared file_list for source and destination.
    :return: files list in source whose hash is different from destination
    OR if file in destination has no hash.
    """
    src_dict = {}
    dst_dict = {}
    for file in file_list:
        src_dict[file], updated = dict_mount(src_sha1.path, file, src_sha1.array,
                                             buffer, quiet, log, need_update=True)
        dst_dict[file], _ = dict_mount(dst_sha1.path, file, dst_sha1.array,
                                       buffer, quiet, log, need_update=False)
        if updated:
            src_sha1.array[file] = src_dict[file]
    diff_list = [name for name, sha1 in dst_dict.items() if src_dict[name.rstrip()] != sha1]
    return diff_list


def sha1_write(path, name, bufsize, quiet, log):
    q = queue.Queue()
    hash_array = {}
    block_counter = 0
    buffer = (bufsize if 2 ** 20 < bufsize < 2 ** 30
              else 100 * (2 ** 20))  # 1MB - 1GB else 100MB

    class Block:
        def __init__(self, number, data):
            self.number = number
            self.data = data

    def worker():
        while True:
            sha = hashlib.sha1()
            item = q.get()
            sha.update(item.data)
            item.data = None
            hash_array[item.number] = sha.digest()
            q.task_done()

    filename = Path(f"{path}\\{name}")
    print_out(f"Generating hash for: {filename}", quiet, log)
    threads = 3 if os.cpu_count() >= 4 else 2
    for _ in range(threads):
        threading.Thread(target=worker, daemon=True).start()
    with open(filename, mode='rb') as file:
        while True:
            try:
                block = Block(block_counter, file.read(buffer))
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
    return sha1.hexdigest()


def print_out(msg, quiet, log):
    if not quiet:
        print(f"{msg}")
    if log:
        logging.debug(f"{msg}")
