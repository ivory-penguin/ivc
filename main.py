"""
during development you can run:
pwsh:   function ivc { py main.py @args }
debian: alias ivc="python-3 main.py"
in pwsh in the root dir to setup the CLI correctly
"""

import argparse
import menu

if __name__ == "__main__":
    # figuring out args
    parser = argparse.ArgumentParser("ivc", description="Ivc is a version control system designed to be simple to use, but providing deeper functionality and using minimal storage space. Also I needed some more projects to put on a portfolio so here we are", usage="ivc [FUNCTION] [PARAMETERS]")
    sub_parsers = parser.add_subparsers(title="Options")

    backup_parser = sub_parsers.add_parser("backup", usage="ivc backup [project] [-n name] [-d description]", help="Creates a backup of the specified project")
    backup_parser.add_argument("project", help="the name of the project that you are backing up")
    backup_parser.add_argument("-n", "--name", help="the name of the new version ")
    backup_parser.add_argument("-d", "--description", help="the description of th new version (should be placed into a \'string\')")
    backup_parser.set_defaults(func=menu.BackupProject)

    rollback_parser = sub_parsers.add_parser("rollback", usage="ivc rollback [project] [version name]", help="Rolls back the selected project to the selected version")
    rollback_parser.add_argument("project", help="the name of the project that you are rolling back")
    rollback_parser.add_argument("version", help="the name of the version that you are rolling back to")
    rollback_parser.set_defaults(func=menu.RollbackProject)

    create_parser = sub_parsers.add_parser("create", usage="ivc create [project name] [root directory]", help="Creates a project under the specified alias name in the directory")
    create_parser.add_argument("project", help="the name of the project that you are creating")
    create_parser.add_argument("root_directory", help="the root directory where the project is stored (note that this cannot be changed at a later date)")
    create_parser.set_defaults(func=menu.CreateNewProject)

    tree_parser = sub_parsers.add_parser("tree", usage="ivc tree [project]", help="Displays the version tree for the selected project")
    tree_parser.add_argument("project", help="the project which you want to view the verison tree for")
    tree_parser.set_defaults(func=menu.DisplayTree)

    GUI_parser = sub_parsers.add_parser("GUI", usage="ivc GUI", help="loads into the GUI version of ivc")
    GUI_parser.set_defaults(func=menu.MainLoop)

    list_parser = sub_parsers.add_parser("list", usage="ivc list", help="list recognized projects or information about versions")
    list_parser.add_argument("-v", "--version", help="lists information about the specified project version. requires 2 arguments (ivc list -v [project] [version])", nargs=2)
    list_parser.set_defaults(func=menu.ListProjects)

    args = parser.parse_args()

    # default case we load into GUI
    if not hasattr(args, "func"):
        menu.MainLoop()
        quit()
    
    if hasattr(args, "project") and args.func != menu.CreateNewProject:
        menu.current_project = args.project
        with open("VC data/projects.txt") as file:
            for line in file.readlines():
                if args.project == line.split("|")[0]:
                    break
            else:
                print(f"{args.project} is not recognized. ")
                quit()
    print(args)
    args.func(args=args)



"""
Rough CLI plan:
ivc [function] [project] [parameters]

:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:
: Functions   : Command Example                                   : Explanation                                                                                                                                                                                       :
:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:
: backup      : ivc backup [project] [-n version name -d details] : Creates a backup of the specified project. optional name can be added to make it easier to view the tree and rollback later. optional details can be added to add any extra info to the version   :
: rollback    : ivc rollback [project] [version name]             : Rolls back the selected project to the selected version. recommended to call IVC tree first                                                                                                       :
: create      : ivc create [project] [root dir]                   : Creates a project under the specified alias name in the directory and creates an empty V0001                                                                                                      :
: tree        : ivc tree [project]                                : Displays the version tree for the selected project                                                                                                                                                :
: GUI         : ivc GUI                                           : Loads into the ivc GUI version                                                                                                                                                                    :
: list        : ivc list [-v project version]                     : Lists recognized projects, or lists the information on project version such as name and description                                                                                               :
: remove      : ivc remove [project]                              : removes the project from ivc, deleting all backups and removing it from the project list                                                                                                          :
:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:

"""