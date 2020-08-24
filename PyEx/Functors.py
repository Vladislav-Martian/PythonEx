from PyEx.Events import delegate, Event, evented
from PyEx.Errors import Error, AccessError, instry
#===============================================
#===============================================


class NotCallableError(Error):
    pass
#===============================================
__all__ = [
    "scf",
    "service"
]
cont = {
    "services": {},
    "namegen": 0
}
def scf(forn=None):
    '''Tool to make some functions service-oriented.
    just removes function from global (replace to None) and call it by service.name()
    '''
    if callable(forn):
        if hasattr(forn, "__name__"):
            cont["services"][getattr(forn, "__name__")] = forn
            return None
        else:
            cont["services"][f"service{cont['namegen']}"] = forn
            cont["namegen"] += 1
            return None
    elif isinstance(forn, str):
        def wrapper(func):
            cont["services"][forn] = func
            return None
        return wrapper
    else:
        raise NotCallableError("object are not callable")
class tech0(object):
    def __init__(self, func):
        self.__gter__ = func

    def __getattr__(self, key):
        return self.__gter__(key)
service = tech0(lambda key: cont["services"][key])
