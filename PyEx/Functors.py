from PyEx.Events import delegate, Event, evented
from PyEx.Errors import Error, AccessError, instry
#===============================================
#===============================================


class NotCallableError(Error):
    pass
class ComplexError(Error):
    pass
#===============================================
__all__ = [
    "scf",
    "service",
    "functor"
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
#=====================================================
class EventCall(Event):
    pass
class EventCallError(Event):
    pass

class functor(evented):
    def __init__(self, cb, name=None, doc="NoDescription", **kwargs):
        self.__additiveattrs__ = {}
        self.workers = delegate()
        if not callable(cb):
            raise NotCallableError("Object are not callable")
        self.workers.add(cb)
        if name == None:
            name = cb.__name__
        else:
            name = str(name)
        self.__name__ = name
        if hasattr(cb, "__doc__"):
            doc = cb.__doc__
        self.__doc__ = doc
        self.addevents(call=0, error=0)
        self.lockeventextending()
        self.data = {}
        self.context = None
        self.isnew = False
        self.addAttributes(**kwargs)
    
    def addAttributes(self, **kwargs):
        for key in kwargs:
            self.__additiveattrs__[key] = kwargs[key]
        return self
    
    def reset(self):
        self.isnew = False
        self.context = None

    def on(self, context):
        self.context = context
        return self
    
    def callon(self, context, *args, **kwargs):
        self.context = context
        return self(*args, **kwargs)
    
    def new(self, *args, **kwargs):
        self.isnew = True
        return self(*args, **kwargs)
    
    def __call__(self, *args, **kwargs):
        res = self.workers.invoke(self, *args, **kwargs)
        if len(self.workers.errors) > 0:
            self.eventlaunch("error", EventCallError(args, kwargs, errors=self.workers.errors))
            raise ComplexError("Some errors happend on functor call", *self.workers.errors)
        self.eventlaunch("call", EventCall(args, kwargs, returned=res))
        self.reset()
        return res

    @property
    def name(self):
        return self.__name__
    @name.setter
    def name(self, name):
        self.__name__ = str(name)
    @name.deleter
    def name(self):
        self.__name__ = "Unnamed"
    
    @property
    def doc(self):
        return self.__name__
    @doc.setter
    def doc(self, doc):
        self.__doc__ = str(doc)
    @doc.deleter
    def doc(self):
        self.__doc__ = "NoDescription"
    
    def help(self):
        return self.doc
    
    def __getattr__(self, name):
        if name in self.__additiveattrs__:
            return self.__additiveattrs__[name]
        else:
            raise AttributeError(f"Attribute {name}")
    
    def __setattr__(self, name, val):
        if hasattr(self, name) and name in self.__additiveattrs__:
            self.__additiveattrs__[name] = val
        else:
            self.__dict__[name] = val

    def __delattr__(self, name):
        if hasattr(self, name) and name in self.__additiveattrs__:
            del self.__additiveattrs__[name]
        else:
            del self.__dict__[name]

    def __len__(self):
        return len(self.workers)
    
    def __repr__(self):
        return f"Functor<{self.name}>"

    def create(self, arg1, arg2="NoDescription", **kwargs):
        if callable(arg1):
            return functor(arg1)
        elif isinstance(arg1, str):
            def wrapper(func):
                return functor(func, arg1, arg2, **kwargs)
            return wrapper
        else:
            raise Error("Wrong arguments")
