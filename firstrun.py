import os
def CreateFilesAndDirs():
    with open("cached info/files and dirs.txt") as file:
        for path in file.read():
            if '.' in path.split('\\')[-1]:
                # if a file, create it if it doesn't exist
                try:
                    open(path, 'r').close()
                except FileNotFoundError:
                    open(path, 'w').close()

            else:
                # if a dir, try mkdir
                try:
                    os.mkdirs(path)
                except FileExistsError:
                    continue

def Init():
    CreateFilesAndDirs()

    open("firstrun", 'w').close()