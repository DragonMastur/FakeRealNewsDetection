import datetime
import sys

class PiConsole:
    def __init__(self, name="Pi Console"):
        self.name = name

    def printf(self, text, end="\n", name=None):
        if name == None:
            name = self.name
        sys.stdout.write("[{name}] ".format(name=name) + text + end)

    def log(self, text, end="\n"):
        time = datetime.datetime.now().isoformat()
        self.printf(text, end, "LOG "+time+" "+self.name)

    def logerror(self, text, end="\n"):
        time = datetime.datetime.now().isoformat()
        self.printf(text, end, "ERROR "+time+" "+self.name)
