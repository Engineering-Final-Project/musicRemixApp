from remix.project import Project


class Manager:
    _instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Manager._instance is None:
            Manager()
        return Manager._instance

    def __init__(self):
        """ Virtually private constructor. """
        if Manager._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Manager._instance = self
        self._projects = dict()  # {name: project}
        self._curr_project = None  # project

    def create_project(self, name):
        if name in self.get_project_names():
            raise Exception("A remix with this name has already been created")
        pr = Project(name)
        self._projects[name] = pr
        self._curr_project = pr
        return pr

    def get_project(self, name):
        return self._projects[name]

    def get_project_names(self):
        return list(self._projects.keys())

    def get_project_name(self, project):
        for name in self._projects:
            if self._projects[name] == project:
                return name

    def get_projects(self):
        return self._projects

    def get_current_project(self) -> Project:
        return self._curr_project

    def set_current_project(self, pr):
        self._curr_project = pr

    def open_project(self, proj_name):
        """opens the project"""
        if proj_name not in self._projects:
            raise Exception("The selected project does not exist")
        if self._projects[proj_name] is not None:
            self._curr_project = self._projects[proj_name]

    def save(self):
        """saves the project to disk"""
        # https://stackoverflow.com/questions/2709800/how-to-pickle-yourself?msclkid=6d79404ecfa111ec970ed3bce6ed2a97
        # open new file save as wb and open as rb
        # save = dump
        # open = load
        if self._curr_project is None:
            raise Exception("No project has been selected")
        self._curr_project.save()

    def save_project_as(self, save_path):
        """saves the project to disk"""
        if self._curr_project is None:
            raise Exception("No project has been selected")
        self._curr_project.save_as(save_path)

    def remove_project(self):
        """removes the current project from the manager's projects list"""
        if self._curr_project is None:
            raise Exception("The current project does not exist")
        name = self.get_project_name(self._curr_project)
        self._curr_project = None
        return self._projects.pop(name, "This project does not exist")

    def clear(self, proj_name, confirm=True):
        """clears the project"""
        if proj_name not in self._projects:
            return
        if confirm:
            clear = input("Are you sure you want to clear the project? y/n")
            while clear != "y":
                if clear == "n":
                    return
                else:
                    clear = input("Are you sure you want to clear the project? Please enter y or n")
            self._projects.pop(proj_name)


