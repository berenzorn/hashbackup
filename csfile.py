import lib


class File:

    def __init__(self, name, checksum=None):
        self.name = name
        self.checksum = checksum


class CsFile:
    instances = {}
    path = None

    @staticmethod
    def get_instance():
        if CsFile.path not in CsFile.instances:
            CsFile(CsFile.path)
        else:
            return CsFile.instances[CsFile.path]

    def __init__(self, path):
        CsFile.path = path
        if path not in CsFile.instances:
            CsFile.instances[path] = self
        self.array = self.read_file()

    def read_file(self) -> dict:
        cs_array = {}
        try:
            for line in open(f"{self.path}\\.sha1", 'r'):
                file = File(line.split('   ')[1].strip(),
                            line.split('   ')[0].strip())
                cs_array[file.name] = file.checksum
        except FileNotFoundError:
            return cs_array
        return cs_array

    def read_sha1(self, name):
        return self.array[name] if name in self.array else False

    def truncate_file(self):
        try:
            with open(f"{self.path}\\.sha1", 'w') as sha_file:
                sha_file.truncate(0)
        except FileNotFoundError:
            return False

    def add_sha1(self, files: list):
        for x in files:
            self.array[x.name] = x.checksum
        # self.truncate_file()
        # self.write_file()

    def delete_sha1(self, names: list, msg, quiet, log):
        lib.print_out(msg, quiet, log)
        for x in names:
            if x in names:
                del self.array[x]
        # self.truncate_file()
        # self.write_file()

    def write_file(self):
        self.truncate_file()
        with open(f"{self.path}\\.sha1", 'w') as sha_file:
            for index in sorted(self.array):
                sha_file.write(f"{self.array[index]}   {index}\n")

