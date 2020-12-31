import os
import lib
import time
import shutil
import pytest
from csfile import CsFile, File


src = "./test1"
dst = "./test2"


def regen_sha1(names_array, cs_file: CsFile):
    checksums = []
    for x in names_array:
        checksums.append(File(x, lib.sha1_write(cs_file.path, x, 1024, False, False)))
    return checksums


def ready_to_test():
    os.mkdir(src)
    os.mkdir(dst)
    os.chdir(src)
    for x in '2345':
        open(x, 'w')
    os.chdir("../test2")
    for x in '123':
        open(x, 'w')
    os.chdir("..")
    test1 = CsFile.get_instance(src)
    test2 = CsFile.get_instance(dst)
    test1.add_sha1(regen_sha1(['2', '3'], test1))
    test1.write_file()
    test2.add_sha1(regen_sha1(['2', '3'], test2))
    test2.write_file()
    time.sleep(1)


def test_file_array():
    test1 = CsFile.get_instance(src)
    test2 = CsFile.get_instance(dst)
    rl = True
    assert sorted(lib.file_array(test1, rl)) == ['2', '3', '4', '5']
    assert sorted(lib.file_array(test2, rl)) == ['1', '2', '3']
    rl = False
    assert sorted(lib.file_array(test1, rl)) == ['2', '3']
    assert sorted(lib.file_array(test2, rl)) == ['2', '3']


def test_new_files():
    test1 = CsFile.get_instance(src)
    test2 = CsFile.get_instance(dst)
    assert lib.new_files(test1, test2) == (['2', '3'], ['4', '5'], ['1'])


def test_exist_files_check():
    test1 = CsFile.get_instance(src)
    test2 = CsFile.get_instance(dst)
    file_list = lib.new_files(test1, test2)[0]
    # [2, 3], [4, 5], [1]
    buffer = 1024  # 1KB

    def checksum(*args):
        assert lib.exist_files_check(test1, test2, file_list[0], buffer, quiet=False, log=False) == args[0]
        test2.delete_sha1(args[1], "", False, False)
        test2.write_file()
        assert lib.exist_files_check(test1, test2, file_list[0], buffer, quiet=False, log=False) == args[1]
        test2.add_sha1(regen_sha1(args[1], test2))
        test2.write_file()

    checksum([], ['2'])


def test_dict_mount():
    test1 = CsFile.get_instance(src)
    buffer = 1024  # 1KB
    cs_array = test1.array
    assert (lib.dict_mount(src, '2', cs_array, buffer, quiet=False, log=False, need_update=False)
            == ('da39a3ee5e6b4b0d3255bfef95601890afd80709', False))  # empty file checksum
    assert lib.dict_mount(src, '4', cs_array, buffer, quiet=False, log=False, need_update=False) == (0, False)


def test_sha1_wq():
    src = "./test1"
    test1 = CsFile.get_instance(src)
    assert lib.sha1_write(src, '2', 0, quiet=False, log=False) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    assert lib.sha1_write(src, '3', 0, quiet=False, log=False) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    assert lib.sha1_write(src, '3', 0, quiet=True, log=False) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    assert lib.sha1_write(src, '4', 0, quiet=True, log=False) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    test1.delete_sha1(['4'], "", False, False)
    test1.write_file()


def cs_read_file():
    test1 = CsFile.get_instance(src)
    assert test1.read_file() == ['2', '3']


def cs_read_sha1():
    test1 = CsFile.get_instance(src)
    test2 = CsFile.get_instance(dst)
    assert test1.read_sha1('2') == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    assert test2.read_sha1('1') is False


if __name__ == '__main__':
    ready_to_test()
    pytest.main()
    shutil.rmtree(src)
    shutil.rmtree(dst)
