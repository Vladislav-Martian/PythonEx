#===============================================
__all__ = ["Error", "AccessError", "ParsingError", "instry"]
#===============================================
class Error(Exception):
    def __init__(self, message="", *args, **kwargs):
        self.message = str(message)
        self.args = tuple(args)
        self.kwargs = kwargs

    def myclass(self):
        return self.__class__.__name__

    def __str__(self):
        return f"[ {self.myclass()} ] - {self.message} - a/k = ({len(self.args)} / {len(self.kwargs)})"

    def __repr__(self):
        return f"[ {self.myclass()} ] - {self.message} - a/k = ({len(self.args)} / {len(self.kwargs)})"

    def __present__(self, full=True):
        res = f"[ {self.myclass()} ] - {self.message} - a/k = ({len(self.args)} / {len(self.kwargs)})"
        if (len(self.args) + len(self.kwargs)) <= 0 or full == False:
            return res
        else:
            res += "\n"
        if len(self.args):
            for arg in self.kwargs:
                res += f"Kwarg: {arg} > {repr(self.kwargs[arg])}\n"
        if len(self.args):
            for arg in self.args:
                res += f"Argument: {repr(arg)}\n"

    def txt(self):
        res = f"[ {self.myclass()} ] - {self.message} - a/k = ({len(self.args)} / {len(self.kwargs)})"
        if (len(self.args) + len(self.kwargs)) <= 0:
            return res
        else:
            res += "\n"
        if len(self.args):
            for arg in self.kwargs:
                res += f"Kwarg: {arg} > {repr(self.kwargs[arg])}\n"
        if len(self.args):
            for arg in self.args:
                res += f"Argument: {repr(arg)}\n"

class AccessError(Error):
    pass

class ParsingError(Error):
    pass

class TypingError(Error):
    pass


def instry(var, *types, none=False):
    if isinstance(var, tuple(types)) or (none and var == None):
        return True
    raise TypingError(f"Wrong type on value [{repr(var)}]", instance=tuple(types))
