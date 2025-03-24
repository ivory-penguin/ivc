import difflib
import os
import shutil
import json
# updates a line in the cached session data file. line num starts at 1
def UpdateSessionCache(value, line_No):
    # get the lines initially because idk how r+ works
    with open("cached info/previous session.txt", 'r') as file:
        lines = file.readlines()

    with open("cached info/previous session.txt", 'w') as file:
        # write the same data up to the line
        for i in range(line_No - 1):
            file.write(lines[i])

        # write the value
        file.write(value + "\n")

        # write the rest of the file so it doesn't delete itself on close
        for i in range(line_No, len(lines)):
            file.write(lines[i])

# returns if success or fail
def CreateProject(project_name, folder_path) -> bool:
    with open("VC data/projects.txt", 'r') as file:
        for line in file.readlines():
            if line.split('|')[1].strip('\n') == folder_path:
                print(f"you already have a project in that directory, named {line.split('|')[0]}")
                return 0

    try:
        os.mkdir(f'VC data/{project_name}')
    except FileExistsError:
        print(f"Each project must have a unique name. '{project_name}' already exists")
        return 0
    except PermissionError:
        print(f"Permission denied: Unable to create a directory for '{project_name}'.")
    except:
        print("An unknown error occurred. Aborting project creation")
        return 0

    with open('VC data/projects.txt', 'a') as file:
        file.write(f"{project_name}|{folder_path}\n")

    metadata = {
        "next hash"       : "V0002",
        "current hash"    : "V0001",
        "original hash"   : "V0001",
        "latest hash"     : "V0001"
    }
    metadata = json.dumps(metadata)

    with open(f'VC data/{project_name}/Project Metadata.json', 'w') as file:
        file.write(metadata)
    return CreateInitialBackup(project_name)

def CreateInitialBackup(project_name) -> bool:
    try:
        os.mkdir(f'VC data/{project_name}/V0001')
    except FileExistsError:
        print(f"Each project must have a unique name. '{project_name}' already exists")
        return 0
    except PermissionError:
        print(f"Permission denied: Unable to create a directory for '{project_name}'.")
    except:
        print("An unknown error occurred. Aborting project creation")
        return 0

    metadata = {
        "version name"    : "root",
        "description"     : "an automatic version created by ivc that initialises the project. no files are backed up, and ",
        "hash"            : "V0001",
        "options"         : [],
        "version path"    : [],
        "backed up files" : [],
    }
    metadata = json.dumps(metadata)

    with open(f'VC data/{project_name}/V0001/Version Metadata.json', 'w') as file:
        file.write(metadata)

    return 1

def BackupVersion(project_name, version_name, description):
    # don't try to read this, it's just the words 'version' and 'metadata' 100 times over

    # find the version info
    with open(f'VC data/{project_name}/Project Metadata.json', 'r') as file:
        project_metadata = json.loads(file.read())
    current_version = project_metadata["next hash"]
    previous_version = project_metadata["current hash"]
    with open(f'VC data/{project_name}/{previous_version}/Version Metadata.json', 'r') as file:
        previous_metadata = json.loads(file.read())

    # increment the version and write it back to the project metadata
    project_metadata["current hash"] = project_metadata["next hash"]
    project_metadata["next hash"] = f'V{str(int(current_version[1:]) + 1).zfill(4)}'
    project_metadata["latest hash"] = project_metadata["next hash"]

    new_metadata = json.dumps(project_metadata)
    with open(f'VC data/{project_name}/Project Metadata.json', 'w') as file:
        file.write(new_metadata)

    # update the previous version's options to include this version
    previous_metadata["options"].append(current_version)
    new_metadata = json.dumps(previous_metadata)
    with open(f'VC data/{project_name}/{previous_version}/Version Metadata.json', 'w') as file:
        file.write(new_metadata)

    # create the metadata file
    prev_path = previous_metadata["version path"]
    prev_path.append(len(previous_metadata["options"]) - 1) # add the last option (the one we just appended to point to this version) to get the new node path
    new_path = prev_path

    # find the original directory
    live_file_path = ""
    with open('VC data/projects.txt', 'r') as project_file:
        for line in project_file.readlines():
            line = line.split("|")
            if line[0] == project_name:
                live_file_path = line[1]
                break
    if not live_file_path:
        raise FileNotFoundError (f"Failed to find the live file version in projects.txt for {project_name}")

    # find the files we're backing up inc any new ones
    current_walk = []
    for root, _, files in os.walk(live_file_path):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), live_file_path)
            current_walk.append(relative_path)

    previous_walk = previous_metadata["backed up files"]

    current_metadata = {
        "version name" : version_name,
        "description" : description,
        "hash" : current_version,
        "options" : [],
        "version path" : new_path,
        "backed up files" : current_walk
    }
    current_metadata = json.dumps(current_metadata)
    os.mkdir(f"VC data/{project_name}/{current_version}")
    open(f'VC data/{project_name}/{current_version}/Version Metadata.json', 'w').close()
    with open(f'VC data/{project_name}/{current_version}/Version Metadata.json', 'w') as file:
        file.write(current_metadata)
    # actually find deltas and such
    for file_path in current_walk:
        if file_path in previous_walk:
            # figure out the relative file path from this script
            full_file_path = f'VC data/{project_name}/{current_version}/{file_path}'

            # reconstruct the old file
            ReconstructFile(project_name, previous_version, file_path)

            # get the file deltas
            deltas = GetDeltas(f"{live_file_path}/{file_path}")

            for delta in deltas:
                delta["iv"] = ByteArrayToIntArray(delta["iv"])
                delta["jv"] = ByteArrayToIntArray(delta["jv"])


            # create the new file whilst also creating any directories we might need
            temp_path = file_path.split(os.sep)
            ptr = 0
            while True:
                try:
                    open(f"{full_file_path}.json", 'w').close()
                    break
                except FileNotFoundError:
                    try:
                        os.mkdir(f'VC data/{project_name}/{current_version}/{temp_path[ptr]}')
                        ptr +=1
                    except IndexError:
                        raise PermissionError(f"Unable to write to {full_file_path}, IVC may not have permission to write to files there")

            # write the deltas to the file
            data = json.dumps(deltas)
            with open(f"{full_file_path}.json", 'w') as file:
                file.write(data)

        else:
            # if the file is newly created, we can just insert everything
            full_file_path = f'VC data/{project_name}/{current_version}/{file_path}'

            # empty the reconstructed file instead of reconstructing anything for the unknown file
            open("cached info/reconstructed file", 'w').close()

            # find the insertion delta
            deltas = GetDeltas(f"{live_file_path}/{file_path}")

            for delta in deltas:
                delta["iv"] = ByteArrayToIntArray(delta["iv"])
                delta["jv"] = ByteArrayToIntArray(delta["jv"])
            data = json.dumps(deltas)

            # create the new file whilst also creating any directories we might need
            temp_path = file_path.split("\\")
            ptr = 0
            while True:
                try:
                    open(f"{full_file_path}.json", 'w').close()
                    break
                except FileNotFoundError:
                    try:
                        os.mkdir(f'VC data/{project_name}/{current_version}/{temp_path[ptr]}')
                        ptr += 1
                    except IndexError:
                        raise PermissionError(f"Unable to write to {full_file_path}, IVC may not have permission to write to files there")

            with open(f"{full_file_path}.json", 'w') as file:
                file.write(data)



# finds a file version in the tree and reconstructs it based on stored deltas. Stores that in cached\ info/reconstructed\ file for later usage
# note that the current version cannot be reconstructed this way because it is not backed up in VC data but is stored in the live project version so should be accessed that way instead
def ReconstructFile(project_name, version_hash, relative_file_path):
    # Load the metadata for the version path
    with open(f'VC data/{project_name}/{version_hash}/Version Metadata.json') as file:
        data = json.load(file)
        version_path = data["version path"]

    # Start with an empty bytearray (mutable)
    reconstructed_bytes = bytearray()

    # Follow the version path to reconstruct the file
    version = "V0001"
    for option in version_path:
        # Find the correct version
        with open(f'VC data/{project_name}/{version}/Version Metadata.json') as metadata:
            version = json.load(metadata)["options"][option]

        # try to load the delta file for this version
        try:
            with open(f'VC data/{project_name}/{version}/{relative_file_path}.json', 'r') as version_file:
                deltas: list[dict] = json.load(version_file)
                for delta in deltas:
                    delta["iv"] = IntArrayToByteArray(delta["iv"])
                    delta["jv"] = IntArrayToByteArray(delta["jv"])
        except FileNotFoundError:
            # if the file doesn't exist, it means it is created in a future version so we can just go to the next version
            # also it means that if a file is deleted then recreated it should hopefully not blow up everything
            continue

        # Sort deltas in reverse index order to avoid index shifting issues
        deltas.sort(key=lambda delta: delta["i1"], reverse=True)

        # Apply each delta to reconstruct the file
        for delta in deltas:
            i1, i2, jv = delta["i1"], delta["i2"], delta["jv"]
            match delta["tag"]:
                case "delete":
                    reconstructed_bytes = reconstructed_bytes[:i1] + reconstructed_bytes[i2:]
                case "replace":
                    reconstructed_bytes[i1:i2] = jv
                case "insert":
                    reconstructed_bytes = reconstructed_bytes[:i1] + jv + reconstructed_bytes[i1:]

    # Write reconstructed file
    with open('cached info/reconstructed file', 'wb') as new_file:
        new_file.write(reconstructed_bytes)

# new file is the currently active file path in the OS walk, old file is the reconstructed file which will be found in cached\ info/reconstructed\ file
# as such, only the new file path needs to be provided, alongside reconstructing the old version
def GetDeltas(new_file_path) -> list[dict]:
    # difflib is used here because it's really complicated to do a better solution, even though difflib is designed for human readability rather than minimal deltas
    with open(new_file_path, 'rb') as new_file:
        with open("cached info/reconstructed file", 'rb') as old_file:
            old_bytes = old_file.read()
            new_bytes = new_file.read()

            # refer to the table. I even made it pretty for you
            # each delta is represented as a {tag, i1, i2, j1, j2, iv, jv} dictionary
            # tag is the change. Values are in the first column of the table
            # i1 and i2 are indexes in the a which point to the start and end of the change
            # j1 and j2 are the same for b
            # iv and ij are the values from a[i1:i2] and b[j1:j2] respectively. Stores more data, but should make reconstruction faster
            """
            ┌──────────────────────────────────────────────────────────────┐
            │ tag name  │ to construct b, do the following to a:           │
            ├───────────┼──────────────────────────────────────────────────┤
            │ "delete"  │ delete [i1:i2]                                   │
            │ "replace" │ replace [i1:i2] with jv                          │
            │ "insert"  │ insert jv at [i1]                                │
            └──────────────────────────────────────────────────────────────┘
            """
            matcher = difflib.SequenceMatcher(a = old_bytes, b = new_bytes)

            deltas = []
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                # equal is unchanged (not a delta)
                if tag != 'equal':
                    # i think we only need tag, i1, i2 and jv but i'm storing everything until i prove that
                    deltas.append({
                        "tag" : tag, "i1" : i1, "i2" : i2, "j1" : j1, "j2" : j2, "iv" : old_bytes[i1:i2], "jv" : new_bytes[j1:j2]
                        })
            return deltas



# i thought this was more complicated than it was so i wrote functions for it, then started simplifying until we ended up with these which are already integrated so just ignore them
def ByteArrayToIntArray(byte_array):
    return list(byte_array)
def IntArrayToByteArray(ints):
    return bytes(ints)


# returns true if successful, false if unsuccessful (created a zip) and throws an error if it can do neither
def RollbackVersion(project_name, version_hash):
    # empty the reconstructed version
    shutil.rmtree('cached info/reconstructed version')
    os.mkdir('cached info/reconstructed version')

    # get the data for the version
    with open(f"VC data/{project_name}/{version_hash}/Version Metadata.json",'r') as file_path:
        metadata = json.loads(file_path.read())


    # recreate the directory structure
    reconstructable_files: list[str] = metadata["backed up files"]
    dir_tree: list[set[str]] = []
    for file_path in reconstructable_files:
        # if no dir to create, continue
        if not os.sep in file_path:
            continue

        dirs = file_path.split(os.sep)

        # ignore the file name
        dirs.pop()

        # create the sets of dirs
        for i, dir in enumerate(dirs):
            if len(dir_tree) - 1 <= i:
                dir_tree.append(set())
            dir_tree[i].add(dir)

    # create the dirs we found
    for level in dir_tree:
        for dir in level:
            os.mkdir('cached info/reconstructed version' + os.sep + dir)

    # recreate the files
    for file_path in reconstructable_files:
        # create a blank file for each file
        open('cached info/reconstructed version' + os.sep + file_path, 'w').close()

        # reconstruct each file
        ReconstructFile(project_name, version_hash, file_path)

        # copy the reconstructed file into the file we're recreating
        with open('cached info/reconstructed version' + os.sep + file_path, 'wb') as copy_location:
            with open('cached info/reconstructed file', 'rb') as copy_source:
                copy_location.write(copy_source.read())

    # then we copy it into the correct place instead of cached info/reconstructed version
    # first find the live version
    live_version = ""
    with open("VC data/projects.txt", 'r') as file:
        projects = file.readlines()
        for project in projects:
            if project.split('|')[0] == project_name:
                live_version = project.split('|')[1].strip("\n")
                break


    # make sure the user knows not to kill their live version
    print("Overwriting live files. Please do not close the program or your files may be missing")

    # also update the project metadata to reflect the current version we rolled back to
    with open(f"VC data/{project_name}/Project Metadata.json", "r+") as file:
        metadata = json.loads(file.read())
        metadata["current hash"] = version_hash
        file.seek(0)
        file.write(json.dumps(metadata))


    # shutil being the most useful module ever once again
    try:
        # rmtree should require the same permissions as copytree, so no risk of deletion without overwriting
        shutil.rmtree(live_version)
        shutil.copytree("cached info/reconstructed version", live_version)
        print("Overwriting complete")
        return True
    except PermissionError:
        print("\n ----- error ------")
        print(f"IVC does not have permissions to write to {live_version}, your files have not been overwritten")
        print(f"attempting to create the file in {os.getcwd}{os.sep}project zips{os.sep}{project_name}-{version_hash}\n")
        shutil.make_archive(f"project zips/{project_name}-{version_hash}", 'zip', "cached info/reconstructed version")
        print("please copy or move the file into the live version, delete your current files and unzip the archive to complete the rollback")
        return False

if __name__ == "__main__":
    RollbackVersion("test 21", "V0007")