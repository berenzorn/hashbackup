import pytest
import lib


def test_file_array():

    path = "./test"
    path2 = "./test2"
    rl = True
    from pathlib import WindowsPath
    # "./test" or "./test2", True
    assert lib.file_array(path, rl) == [WindowsPath('test/2'), WindowsPath('test/3'), WindowsPath('test/4')]
    assert lib.file_array(path2, rl) == [WindowsPath('test2/1'), WindowsPath('test2/2'), WindowsPath('test2/3')]
    rl = False
    # "./test" or "./test2", False
    assert lib.file_array(path, rl) == [WindowsPath('test/2.sha1'), WindowsPath('test/3.sha1')]
    assert (lib.file_array(path2, rl) ==
            [WindowsPath('test2/1.sha1'), WindowsPath('test2/2.sha1'), WindowsPath('test2/3.sha1')])


def test_new_files():

    src = "./test"
    dst = "./test2"
    assert lib.new_files(src, dst) == (['2', '3'], ['4'], ['1'])


def test_exist_files_check():
    src = "./test"
    dst = "./test2"
    file_list = lib.new_files(src, dst)[0]
    buffer = 1024  # 1KB

    def checksum(checksum, *args):

        assert lib.exist_files_check(src, dst, file_list, buffer, quiet=False, log=False) == args[0][0]
        with open(checksum, 'r') as sha_file:
            sha_string = sha_file.readline()
        with open(checksum, 'w') as sha_file:
            sha_file.truncate(0)
        assert lib.exist_files_check(src, dst, file_list, buffer, quiet=False, log=False) == args[0][1]
        with open(checksum, 'w') as sha_file:
            sha_file.write(sha_string)

    checksum(f"{src}/2.sha1", ([], ['2']))
    checksum(f"{dst}/3.sha1", ([], ['3']))


def test_dict_mount():
    src = "./test"
    buffer = 1024  # 1KB

    assert (lib.dict_mount(src, '2', buffer, quiet=False, log=False, need_update=False)
            == 'da39a3ee5e6b4b0d3255bfef95601890afd80709')  # empty file checksum
    assert lib.dict_mount(src, '4', buffer, quiet=False, log=False, need_update=False) == 0


def test_sha1_wq():
    src = "./test"

    assert lib.sha1_write_queue(src, '2', 0, quiet=False, log=False) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    assert lib.sha1_write_queue(src, '3', 0, quiet=False, log=False) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    assert lib.sha1_write_queue(src, '3', 0, quiet=True, log=False) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    assert lib.sha1_write_queue(src, '4', 0, quiet=True, log=False) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    import os
    if os.path.exists("./test/4.sha1"):
        os.remove("./test/4.sha1")
    pass


if __name__ == '__main__':
    pytest.main()
