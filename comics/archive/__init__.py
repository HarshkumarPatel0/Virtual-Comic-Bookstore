import sys, rarfile, zipfile, os

class ArchiveFile:

    def __init__(self, info):
        self.info = info
        if isinstance(info, zipfile.ZipInfo):
            self.filename = info.filename
            self.size = info.file_size
        else:
            self.filename = info.filename
            self.size = info.file_size

    @property
    def name(self):
        if "/" in self.filename:
            return self.filename.split("/")[-1]
        return self.filename

    @property
    def extension(self):
        return self.filename.split(".")[-1].lower()

    def __str__(self):
        return f"{self.name} ({self.size} bytes)"

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.filename < other.filename

IMAGES = set("jpg gif png jpeg".split())
IGNORE = set("txt info url torrent".split())
COMIC = set("cbr cbz".split())

class Archive:

    def __init__(self, filename):
        self.type = None
        self.archive = None
        self.files = None
        with open(filename, 'rb') as f:
            hdr = f.read(4)

        try:
            if hdr == b'Rar!':
                self.type = 'rar'
                self.archive = rarfile.RarFile(filename)
            elif hdr[:2] == b'PK':
                self.type = 'zip'
                self.archive = zipfile.ZipFile(filename)
        except Exception as e:
            print("Unable to open", filename)
            print("Exception:", e)

    def __iter__(self):
        if not self.files:
            self.files = sorted([ArchiveFile(f) for f in self.archive.infolist() if not f.is_dir()])
        if self.files:
            yield from self.files

    def isCb(self):
        maybe = 0
        maybeNot = 0
        for file in self:
            ext = file.extension
            if ext not in (IMAGES | IGNORE):
                return None
            if ext in IMAGES:
                maybe += 1
            else:
                maybeNot += 1
        if maybe > 10 and maybe > 3 * maybeNot:
            if self.type == 'rar':
                return "cbr"
            if self.type == 'zip':
                return "cbz"

    def extract(self, dir='.'):
        error = False
        extracted = False
        for file in self:
            ext = file.extension
            if ext in IGNORE:
                continue
            if ext in COMIC:
                try:
                    print("Extracting:", file.name)
                    with open(os.path.join(dir, file.name), "wb") as f:
                        with self.archive.open(file.filename, "r") as src:
                            while True:
                                data = src.read(1024*1024)
                                if data:
                                    f.write(data)
                                else:
                                    break
                    #self.archive.extract(file.filename, path=".")
                    extracted = True
                except Exception as e:
                    print("Error:", e)
                    error = True
            else:
                error = True
        return not error and extracted

    def contents(self):
        for file in self:
            with self.archive.open(file.filename, "r") as src:
                yield file, src

    def close(self):
        self.archive.close()

    def valid(self):
        return self.archive != None


def main(args):
    if len(args) > 1:
        archive = Archive(args[1])
        #for file in archive:
        #   print(file)
        #   archive.extract(file)
        print(args[1],"is cb?", archive.isCb(), "extract?", archive.extract())
        archive.close()


if __name__ == "__main__":
    main(sys.argv)
