import datetime
import sys

class PiConsole:
    def __init__(self, name="Pi Console"):
        self.name = name
        self.filename = "log.txt"

    def configure(self, **kwargs):
        if kwargs != None:
            for key, value in kwargs.iteritems():
                if key == "filename":
                    self.filename = value

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

    def filelog(self, text, end="\n"):
        try:
            with open(self.filename, 'rb') as f_in:
                f_cont = str(f_in.read())
        except:
            f_cont = ""
        f_cont += text + end
        with open(self.filename, 'w') as f_out:
            f_out.write(f_cont)
