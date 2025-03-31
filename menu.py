from time import sleep
import file_operations
import json
import tkinter
from tkinter import filedialog
import re
tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing

current_project = "None"

def Init():
    print("\033c")

    global current_project
    with open("cached info/previous session.txt", 'r') as file:
        current_project = file.readline().strip('\n')

# does menu input function call loop thing until program is killed
def MainLoop(args = None):
    Init()
    while True:
        options = [
            lambda: SelectProject(),
            lambda: BackupProject(),
            lambda: RollbackProject(),
            lambda: CreateNewProject(),
            lambda: DisplayTree(blocking=True),
            lambda: RemoveProject()
        ]
        option = DisplayMenu()
        if option in (1,2,3,4,5,6):
            options[option-1]()
        elif option == 7:
            break
        else:
            print("somehow DisplayMenu returned an unknown value. Fix your stupid program please")
            quit()

# returns menu option. Do function based on number
# replace with GUI and/or CLI later
def DisplayMenu() -> int:
    print(f"""
\033c----- IVC Options -----
currently active project: {current_project}
1. select a different project
2. backup your project
3. load a different project version
4. create a new project
5. view project history tree
6. delete the current project
7. close ivc
enter a number: """, end="")
    option = input()
    while not option.isdigit() or int(option) > 7 or int(option) < 1:
        return int(DisplayMenu())
    return int(option)

def DisplayTree(args = None, blocking: bool = False):
    # screw it, CLI tree
    """
    ━━━V0001━━━V0002━┳━V0003━┳━V0004
                     ┃       ┗━V0007
                     ┗━V0005━━━V0006
    """

    # can be split into columns:
    """
     i0   i1   i2   i3   i4   i5   i6
    V0001|━━━|V0002|━┳━|V0003|━┳━|V0004|
         |   |     | ┃ |     | ┗━|V0007|
         |   |     | ┗━|V0005|━━━|V0006|
    """
    # this feels like a case to use recursion because we're traversing a tree
    # how to recursion good
    # ms paint time
    # HOLY SH-- IT WORKS WITH RECURSION
    # look at the MS paint
    # this is how we can traverse to find every node in the tree in the ideal order where each node knows its position
    # this should allow us to construct:
    """
    |V0001|V0002|V0003|V0004|
    |     |     |     |V0007|
    |     |     |V0005|V0006|
    """
    # joining them is harder though, need to keep track of what points where
    # wait, do we?
    # we can just insert the between layers as we traverse, surely?
    # that sounds super complex
    # does it?
    # set everything to 2x index (adding an empty layer between everything)
    """
    |V0001||V0002||V0003||V0004|
    |     ||     ||     ||V0007|
    |     ||     ||V0005||V0006|
    """
    # we insert at the same height as the child with depth -1
    # if i == 0 and len(self.children) == 1, we can add a "━━━"
    # else if i == 0 and len(self.children) > 1, we can add a "━┳━"
    # else if i == len(self.children) - 1, we can add a " ┗━"
    # else, we can add a " ┣━"
    # and if the difference between our height and the second child's height is greater than 1, for each position vertically between the parent depth and child depth, we can add a " ┃ "
    # which generates:
    """
    |━━━|V0001|━━━|V0002|━┳━|V0003|━┳━|V0004|
    |   |     |   |     | ┃ |     | ┗━|V0007|
    |   |     |   |     | ┗━|V0005|━━━|V0006|
    """

    # how to even print the output
    # might unironically be easier to use ANSI escape codes here to control pointer position
    # also would be easier to give consistent width to make it look like:
    """
    ━━━━━V0001━━━━━V0002━━┳━━V0003━━┳━━V0004
                          ┃         ┗━━V0007
                          ┗━━V0005━━━━━V0006
    """
    # but not necessary
    # super not necessary actually, the cursor position is 3 + ((5 * (depth % 2)) + (3 * ((depth - 1) % 2)))
    # ok, it's not working so we'll try with the equals

    node_positions = []
    # don't even try and read this function, it's a lot of complex recursion just pray that it works
    # i swear if anyone suggests that i make it self balancing so the longest branch is central rather than on the edge, i am going to make them program it
    def RecursiveNightmareFuelTreeConstructor(version, version_height, depth, max_height):
        with open(f"VC data/{current_project}/{version}/Version Metadata.json") as version_file:
            data = json.loads(version_file.read())

        name = data["hash"]
        children = data["options"]

        node_positions.append((name, version_height, depth * 2))
        child_height = version_height
        for i, child in enumerate(children):

            # some fancy rules to determine what connector to use
            if i == 0 and len(children) == 1:
                connector = "━━━━━"
            elif i == 0 and len(children) > 1:
                connector = "━━┳━━"
            elif i == len(children) - 1: # (and i != 0)
                connector = "  ┗━━"
            else:
                connector = "  ┣━━"

            if i > 0:
                max_height += 1
                child_height = max_height

            # connecting longer branches
            if i >= 1:
                if child_height - version_height + i - 1 >= 2:
                    head_height = version_height + i - 1
                    while head_height != child_height:
                        head_height += 1
                        # this currently sometimes overwrites "  ┣━━" branches. cba to fix, going to just patch it instead
                        if ("  ┣━━", head_height, (depth * 2) + 1) not in node_positions:
                            node_positions.append(("  ┃  ", head_height, (depth * 2) + 1))

            node_positions.append((connector, child_height, (depth * 2) + 1))
            # only add 1 to depth because we have a 2x at the top of the function so it functions as a +2
            max_height = RecursiveNightmareFuelTreeConstructor(child, child_height, depth + 1, max_height)


        # we pass max height around because using global variables and nested functions is a little confusing
        return max_height
    tree_height = RecursiveNightmareFuelTreeConstructor("V0001", 0, 0, 0)
    print("\n" * tree_height, end="")
    UP   = "\033[A"
    DOWN = "\033[B"
    RIGHT= "\033[C"
    LEFT = "\033[D"
    # establish the stem of the tree
    print(UP * tree_height + "━━━━━", end="")
    node_positions.append(("", tree_height+1, -1)) # tells the cursor to go to the end of the tree after printing
    # track cursor position
    cursor_position = [5, 0]
    for node in node_positions:
        # align the heights
        while cursor_position[1] > node[1]:
            print(UP, end="")
            cursor_position[1] -= 1

        while cursor_position[1] < node[1]:
            print(DOWN, end="")
            cursor_position[1] += 1

        # align the depths
        # fancy equation turns grid coordinates into terminal coordinates based on the alternating rows of width 3 and 5
        node = node[0], node[1], 5 + (5 * node[2])
        while cursor_position[0] > node[2]:
            print(LEFT, end="")
            cursor_position[0] -= 1

        while cursor_position[0] < node[2]:
            print(RIGHT, end="")
            cursor_position[0] += 1

        print(node[0], end="")
        cursor_position[0] += len(node[0])
    if blocking and not args:
        input("press enter to return to the menu")
    else:
        print(DOWN)

def SelectProject():
    with open("VC data/projects.txt") as file:
        projects = [project.split("|") for project in file.readlines()]

    print(" ----- Projects: ----- ")
    print("0: cancel selection")
    for i, project in enumerate(projects, start=1):
        print(f"{i}: {project[0]}")
    option = input("please choose a number to select a project ")
    while True:
        if option.isdigit() is False or int(option) < 0 or int(option) > len(project):
            option = input("please enter a valid number ")
        else:
            option = int(option)
            break
    if option == 0:
        return
    global current_project
    current_project = projects[option - 1][0]

    with open("cached info/previous session.txt", 'r') as file:
        lines = file.readlines()

    with open("cached info/previous session.txt", 'w') as file:
        file.write(current_project)
        for line in lines[1:]:
            file.write(line)

    input("project selected successfully. press enter to return to the menu ")

def BackupProject(args = None):
    print(f"backing up {current_project}")
    name = input(f"what name do you want to assign to this version? ") if not hasattr(args, "name") else args.name
    description = input(f"enter a description of the changes made in this version ") if not hasattr(args, "description") else args.description
    file_operations.BackupVersion(current_project, name, description)
    print("project backed up successfully")
    if not args:
        input("press enter to return to the menu")
    return

def RollbackProject(args = None):
    try:
        if not args:
            print("enter ^C (ctrl + C) at any time to cancel rollback (this will close IVC)")
            input(f"rolling back {current_project}. press enter to confirm")

        # temporary list of versions. replace with tree at later date
        with open(f"VC data/{current_project}/Project Metadata.json") as file:
            highest_version = json.loads(file.read())["latest hash"]
            highest_version = highest_version[1:]
            highest_version = int(highest_version)

        if not args:
            DisplayTree()
            version = input("which version would you like to roll back to? enter the version number (e.g V0012) or the version name: ")
        else:
            version = args.version

        valid_inputs = {
            f'V{str(i+1).zfill(4)}' : f'V{str(i+1).zfill(4)}' for i in range(highest_version)
        }

        # we make a copy to iterate through here
        for key in [key for key in valid_inputs.keys()]:
            with open(f"VC data/{current_project}/{key}/Version Metadata.json") as file:
                data = json.loads(file.read())
                valid_inputs[data["version name"]] = key
        # input validation
        while not version in valid_inputs.keys():
            if not args:
                version = input("please re-enter the version: ")
            else:
                print(f"version not recognised. try running 'ivc tree {current_project}' to check what versions are recognised")
                quit()

        version = valid_inputs[version]

        # actually do the rollback
        if file_operations.RollbackVersion(current_project, version):
            if not args:
                input("version rolled back successfully! press enter to return to the menu. ")
        else:
            if not args:
                input("It is not recommended to use IVC until you have unzipped the archive properly. press enter to return to the menu.")
            else:
                print("WARNING: rollback has failed. a zip has been created, please unzip into your project directory, otherwise ivc may have to copy your entire project")
    except KeyboardInterrupt:
        # don't throw a stack trace at the user, please
        quit()

def CreateNewProject(args = None):
    if not hasattr(args, "project"):
        project_name = input("enter the name of your project: ")
        print("please select the directory where your project is located")
        folder_path = filedialog.askdirectory()
    else:
        project_name = args.project
        folder_path = args.root_directory

    if not file_operations.CreateProject(project_name, folder_path):
        # error message is in CreateProject(), no need for one here
        if not args:
            input("Press enter to return to the menu ")
        return

    if not args:
        global current_project
        current_project = project_name
        file_operations.UpdateSessionCache(project_name, 1)
    print("project created successfuly")
    if not args:
        print("the project has been automatically selected as your current project")
    print("It is recommended to create an initial backup")
    if not args:
        input("Press enter to return to the menu ")

    return

def ListProjects(args = None):
    if not hasattr(args, "version"):
        # list projects
        with open("VC data/projects.txt") as file:
            for line in file.readlines():
                print(line.split("|")[0])
    else:
        # list version info
        try:
            # check if we've got a version number or a name
            if not re.search("V\d\d\d\d", args.version[1]):
                # if we have a version name, convert to version number
                # to do this, unfortuantely the fasest way is to just check every version
                with open(f'VC data/{args.version[0]}/Project Metadata.json') as file:
                    max_version = json.loads(file.read())["latest hash"]
                max_version = int(max_version[1:])

                # go through each version and read the data
                for i in range(max_version):
                    version = 'V' + str(i+1).zfill(4)
                    with open(f"VC data/{args.version[0]}/{version}/Version Metadata.json") as file:
                        data = json.loads(file.read())

                        # if it's the right version, get the hash and continue as though the version number was inputed instead of name
                        if data["version name"] == args.version[1]:
                            args.version[1] = data["hash"]
                            break


            with open(f"VC data/{args.version[0]}/{args.version[1]}/Version Metadata.json") as file:
                data = json.loads(file.read())
                print(f"Version Name:       {data['version name']}")
                print(f"Decription:         {data['description']}")
                print(f"Version Code:       {data['hash']}")
                print(f"No. Child Versions: {len(data['backed up files'])}")
                print(f"Stored Files:       ", end="")
                for file in data["backed up files"]:
                    print(file)
        except FileNotFoundError:
            print("Could not find the specified version. Check over your input")

def RemoveProject(args = None):
    valid = input(f"are you sure that you want to delete {current_project}? this cannot be undone. enter 'no' to cancel: ").lower().strip()
    if valid == "no":
        print("aborting deletion.")
        return
    file_operations.RemoveProject(current_project)
    print("project deleted successfully")
    if not args:
        input("press enter to return to the menu")

if __name__ == "__main__":
    Init()
    MainLoop()
