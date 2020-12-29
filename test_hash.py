import pytest
import lib


def test_read_cs_file():
    path1 = "./test1"
    path2 = "./test2"
    assert lib.read_cs_file(path1) == {'2': 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
                                       '3': 'da39a3ee5e6b4b0d3255bfef95601890afd80709'}
    assert lib.read_cs_file(path2) == {'1': 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
                                       '2': 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
                                       '3': 'da39a3ee5e6b4b0d3255bfef95601890afd80709'}


def test_file_array():

    path1 = "./test1"
    path2 = "./test2"
    rl = True
    # "./test1" or "./test2", True
    assert sorted(lib.file_array(path1, rl)) == ['2', '3', '4']
    assert sorted(lib.file_array(path2, rl)) == ['1', '2', '3']
    rl = False
    # "./test1" or "./test2", False
    assert sorted(lib.file_array(path1, rl)) == ['2', '3']
    assert sorted(lib.file_array(path2, rl)) == ['1', '2', '3']


def test_new_files():
    src = "./test1"
    dst = "./test2"
    assert lib.new_files(src, dst) == (['2', '3'], ['4'], ['1'])


def test_exist_files_check():
    src = "./test1"
    dst = "./test2"
    file_list = lib.new_files(src, dst)[0]
    buffer = 1024  # 1KB

    def checksum(*args):
        assert lib.exist_files_check(src, dst, file_list, buffer, quiet=False, log=False) == args[0]
        cs_array = lib.read_cs_file(src)
        lib.sha1_remove(src, args[1], "", False, False)
        assert lib.exist_files_check(src, dst, file_list, buffer, quiet=False, log=False) == []
        lib.update_cs_file(src, args[1][0], cs_array[args[1][0]])

    checksum([], ['2'])
    checksum([], ['3'])


def test_dict_mount():
    src = "./test1"
    buffer = 1024  # 1KB
    cs_array = lib.read_cs_file(src)
    assert (lib.dict_mount(src, '2', cs_array, buffer, quiet=False, log=False, need_update=False)
            == ('da39a3ee5e6b4b0d3255bfef95601890afd80709', False))  # empty file checksum
    assert lib.dict_mount(src, '4', cs_array, buffer, quiet=False, log=False, need_update=False) == (0, False)


def test_sha1_wq():
    src = "./test1"

    assert lib.sha1_write_queue(src, '2', 0, quiet=False, log=False) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    assert lib.sha1_write_queue(src, '3', 0, quiet=False, log=False) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    assert lib.sha1_write_queue(src, '3', 0, quiet=True, log=False) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    assert lib.sha1_write_queue(src, '4', 0, quiet=True, log=False) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    lib.sha1_remove(src, '4', "", False, False)



if __name__ == '__main__':
    pytest.main()
    # print(test_exist_files_check())
