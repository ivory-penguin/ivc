idk what to put here, the thing isn't done being made yet
will exist in more detail when i have everything setup

these functions:

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
