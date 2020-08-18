#===============================================
__all__ = ["delegate", "Event", "evented"]
#===============================================
def fdummy():
    pass
class cdummy:
    invoke = None
    def mdummy(self):
        pass

class delegate(object):
    """Similar to c# delegates its containerfor one or more functions. By default delegate can contain infinite functions, but first argument changes limit. 0 or less to infinity.
    To invoke it just call delegate as functor or use .invoke() method
    .slots      [list] - container with functions to call
    .errors     [list] - errors got on last invoke
    .limit      [int] - limit to count of functions inside delegate
    .invoked    [int] - number of times ivoked"""
    def __init__(self, limit=0, *funcs):
        self.slots = []
        self.errors = []
        self.limit = int(limit)
        self.invoked = 0
        i = 0
        for func in funcs:
            if not callable(func):
                continue
            if self.limit > 0 and i >= limit:
                break
            self.slots.append(func)
            i += 1
    
    def invoke(self, *args, **kwargs):
        """Invokes delegate and each function inside with some arguments. Returns last returned value"""
        ret = None
        buf = None
        self.invoked += 1
        self.errors.clear()
        for func in self.slots:
            try:
                buf = func(*args, **kwargs)
                if buf != None:
                    ret = buf
            except Exception as err:
                self.errors.append(err)
        return ret
    def __call__(self, *args, **kwargs):
        """Invokes delegate and each function inside with some arguments. Returns last returned value"""
        ret = None
        buf = None
        self.invoked += 1
        self.errors.clear()
        for func in self.slots:
            try:
                buf = func(*args, **kwargs)
                if buf != None:
                    ret = buf
            except Exception as err:
                self.errors.append(err)
        return ret
    
    def __len__(self):
        return len(self.slots)
    
    def __repr__(self):
        return f"Delegate [{len(self.slots)} / {self.limit if self.limit > 0 else 'inf'}]"

    def __str__(self):
        return f"Delegate [{len(self.slots)} / {self.limit if self.limit > 0 else 'inf'}]"
    
    def clear(self):
        self.slots.clear()
        return self

    def add(self, *funcs):
        """add fuctions to delegate"""
        i = len(self.slots)
        for func in funcs:
            if not callable(func):
                continue
            if self.limit > 0 and i >= self.limit:
                raise OverflowError(f"Slots are full [{len(self.slots)} / {self.limit}]")
            self.slots.append(func)
            i += 1
        return self
    
    def pop(self):
        """Pop last added function from delegate"""
        return self.slots.pop()
    
    def popinvoke(self, *args, **kwargs):
        """Pop last added function from delegate and call it"""
        return self.slots.pop()(*args, **kwargs)
    
    def remove(self, func):
        """Remove all function links from delegate"""
        while func in self.slots:
            self.slots.remove(func)
        return self
    
    def merge(self, other):
        """Merge 2 delegates to one"""
        if self.limit <= 0 or other.limit <= 0:
            return delegate(0, *(self.slots + other.slots))
        return delegate((self.limit + other.limit), *(self.slots + other.slots))
    
    def __add__(self, func):
        if isinstance(func, delegate):
            return self.merge(func)
        i = len(self.slots)
        if not callable(func):
            return self
        if self.limit > 0 and i >= self.limit:
            raise OverflowError(f"Slots are full [{len(self.slots)} / {self.limit}]")
        self.slots.append(func)
        return self
    
    def __radd__(self, func):
        if isinstance(func, delegate):
            return self.merge(func)
        i = len(self.slots)
        if not callable(func):
            return self
        if self.limit > 0 and  i >= self.limit:
            raise OverflowError(
                f"Slots are full [{len(self.slots)} / {self.limit}]")
        self.slots.append(func)
        return self
    
    def __iadd__(self, func):
        if isinstance(func, delegate):
            return self.merge(func)
        i = len(self.slots)
        if not callable(func):
            return self
        if self.limit > 0 and i >= self.limit:
            raise OverflowError(
                f"Slots are full [{len(self.slots)} / {self.limit}]")
        self.slots.append(func)
        return self
    
    def __sub__(self, func):
        return self.remove(func)
    
    def __isub__(self, func):
        return self.remove(func)

class Event(object):
    """Basic class as event arguments package.
    .this       [any] - event call source
    .like       [str] - Event name
    .handled    [int] - times used method handle
    .args       [list] - args list
    .kwargs     [dict] - dict of key-val pairs"""
    globalhandler = delegate(0)
    def __init__(self, *args, **kwargs):
        self.this = None
        self.like = self.__class__.__name__
        self.kwargs = kwargs
        self.args = args
        self.handled = 0
    
    def on(self, o):
        """Setter for .this property"""
        self.this = o
        return self
    
    def to(self, txt):
        """Setter for .like property"""
        self.like = str(txt)
        return self
    
    def handle(self, handler=None):
        """Handlig for event object"""
        if handler == None:
            handler = Event.globalhandler
        self.handled += 1
        if callable(handler):
            handler(self)
        else:
            Event.globalhandler(self)
    
    def __call__(self, handler=None):
        if handler == None:
            handler = Event.globalhandler
        self.handled += 1
        if callable(handler):
            handler(self)
        else:
            Event.globalhandler(self)
    
    def __repr__(self):
        return f"{self.__class__.__name__} as <{self.like}> on {repr(self.this)} [{self.handled}]"

def most(x, y):
    return x if x >= y else y

class evented(object):
    """<object> class alternative. Advanced with some methods to work with evented containers. Can be used as interface."""
    __events__ = None
    __eventaddlocker__ = False
    
    def subscribe(self, **kwargs):
        """Add functions to delegates by names as key and functions or tuple of functions as value"""
        if not hasattr(self, "__events__") or self.__events__ == None:
            self.__events__ = {}
        for key in kwargs:
            if isinstance(kwargs[key], (tuple, list)):
                if not key in self.__events__:
                    raise Exception(f"Event <{key}> does not exist and can`t be launched")
                elif self.__events__[key] == None:
                    raise Exception(f"Event <{key}> is global")
                self.__events__[key].add(*kwargs[key])
            elif callable(kwargs[key]):
                if self.__events__[key] == None:
                    raise Exception(f"Event <{key}> is global")
                self.__events__[key].add(kwargs[key])
    
    def addevents(self, **events):
        """Adds new events to self object"""
        if hasattr(self, "__eventaddlocker__") and getattr(self, "__eventaddlocker__") == True:
            raise Exception("Access locked. Unposible to add new events by this way.")
        if not hasattr(self, "__events__") or self.__events__ == None: self.__events__ = {}
        self.__events__.update(events)
        for key in self.__events__:
            self.__events__[key] = delegate(most(int(self.__events__[key]), 0))
        return self
    
    def lockeventextending(self):
        """Disallows adding new events to object"""
        self.__eventaddlocker__ = True
    
    def eventlaunch(self, name, event=None):
        """Launches some event with Event object or without (invoke delegate with None argument)"""
        if not hasattr(self, "__events__") or self.__events__ == None:
            self.__events__ = {}
        if not isinstance(event, Event) and not event == None:
            raise ValueError("Non-Event object")
        elif event == None:
            if name in self.__events__ and self.__events__ != None:
                self.__events__[name].invoke(None)
            elif self.__events__ == None:
                Event.globalhandler.invoke(None)
            else:
                raise Exception(f"Event <{name}> does not exist and can`t be launched")
        else:
            if name in self.__events__ and self.__events__ != None:
                event.on(self).to(name).handle(handler=self.__events__[name])
            elif self.__events__ == None:
                Event.globalhandler.invoke(event.on(self).to(name))
            else:
                raise Exception(f"Event <{name}> does not exist and can`t be launched")
    
    def eventdelegate(self, name, globalize=False):
        """Get link to event delegate. With truly secons argument - makes event global (Event.globalhandler delegate)"""
        if not hasattr(self, "__events__") or self.__events__ == None:
            self.__events__ = {}
        if name in self.__events__:
            if globalize:
                self.__events__[name] = None
                return Event.globalhandler
            return self.__events__[name]
        else:
                raise Exception(f"Event <{name}> does not exist and can`t be launched")
#=========================================================================
