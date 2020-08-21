from PyEx.Events import delegate, Event, evented
from PyEx.Errors import Error, AccessError, ParsingError, TypingError, instry
#===============================================
__all__ = ["Node"]
#===============================================
class NodeConstructionError(Error):
    pass

class EventInvoking(Event):
    pass
#===============================================
class Node(evented):
    __counter__ = 0
    '''Class <Node>. Container to functions

    Static:
        None

    Constructor:
        >> Node(func, ?name, ?desc):
            [any.callable] func - link to function. method or functor as core of node

    Attributes:
        [any.callable] __core__ - core function of node
        [dict] __subs__ - subnodes inside
        [Node || =None] __parent__ - parent node link
        [str] __desc__ - description of node
        [str] __inname__ - name of node to call it as sub-node
        [bool] __case__ - Is node case-sensitive

    In-Services:
        static [str] __counter__ - used to automatically generate names to unnamed functor or lambda nodes
    '''
    def __init__(self, func, name=None, desc=None):
        instry(name, str, none=True)
        instry(desc, str, none=True)
        if not callable(func):
            raise NodeConstructionError("Need function, method or functor to construct node")
        # get name from func name or generate it
        if name == None:
            if hasattr(func, "__name__"):
                name = getattr(func, "__name__")
            else:
                name = f"function{Node.__counter__}"
                Node.__counter__ += 1
        # get description from docstring or use ""
        if desc == None:
            if hasattr(func, "__doc__"):
                desc = getattr(func, "__doc__")
            else:
                desc = f"Description for function [{name}]"
        # arguments... Done
        # Events:
        #     invoking - event launches on every node call
        self.addevents(invoking=0)
        self.lockeventextending()
        # setup attributes:
        self.__core__ = func
        self.__parent__ = None
        self.__subs__ = {}
        self.__desc__ = desc
        func.__doc__ = desc
        self.__inname__ = name
        self.__case__ = True
    
    # Standart:
    def __bool__(self):
        return True
    def __repr__(self):
        return f"[{'RootNode' if self.__parent__ == None else 'Sub-Node'}]{self.__inname__}"
    def __str__(self):
        return f"[{'RootNode' if self.__parent__ == None else 'Sub-Node'}]{self.__inname__}"
    def __len__(self):
        return self.grade()
    def __contains__(self, name):
        if self.__case__:
            return name in self.__subs__
        else:
            name = name.lower()
            for key in self.__subs__:
                if key.lower() == name:
                    return True
            return False
    # informators
    def grade(self):
        i = 0
        pos = self
        while pos.__parent__ != None:
            i += 1
            pos = pos.__parent__
        return i
    # predictors
    def isRoot(self):
        return self.__parent__ == None
    def isSubNode(self):
        return self.__parent__ != None
    # navigators
    def goParent(self):
        return self.__parent__ or self
    def goUp(self, i=1):
        pos = self
        i = int(i)
        while i > 0 and pos.__parent__ != None:
            pos = pos.__parent__
            i -= 1
        return pos
    def goRoot(self):
        pos = self
        while pos.__parent__ != None:
            pos = pos.__parent__
        return pos
    # setters & getters
    def getParent(self):
        return self.__parent__
    def getSubNode(self, name):
        if self.__case__ and name in self.__subs__:
            return self.__subs__[name]
        elif not self.__case__ and name in self:
            nm = name.lower()
            for key in self.__subs__:
                if key.lower() == nm:
                    self.__subs__[key]
        else:
            raise AccessError(f"Sub-node '{name}' does not exist")
    # methods
    def insertNode(self, node):
        instry(node, Node)
        self.__subs__[node.__inname__] = node
        node.__parent__ = self
        return node
    def extractNode(self, node):
        instry(node, Node)
        if node.__inname__ in self.__subs__:
            del self.__subs__[node.__inname__]
            node.__parent__ = None
            return node
        else:
            return node
    def setcase(self, case=None):
        if case == None:
            case = not self.__case__
        self.__case__ = bool(case)
        for node in self.__subs__:
            self.__subs__[node].setcase(case)
        return self
    # overloads
    def __call__(self, *args, **kwargs):
        self.__core__(*args, **kwargs)
        self.eventlaunch("invoking", EventInvoking(*args, **kwargs))
    def __getattr__(self, name):
        if name in self:
            return self.getSubNode(name)
        else:
            raise AttributeError(f"Attribute '{name}' does not exists, and sub-node does not exist too")
        
    # static and wrappers
    @staticmethod
    def setup(arg1, arg2=""):
        '''Decorator to convert function to root node
        Using:
        @Node.setup
        def func():
            pass
        
        or:
        @Node.setup([str]name, [str]desc)
        def func():
            pass

        after:
        @func.extend
        def subfunc():
            pass

        or:
        @func.extend([str]name, [str]desc)
        def subfunc():
            pass
        '''
        if callable(arg1):
            return Node(arg1)
        # other way, arg1 is name and arg2 is description
        instry(arg1, str)  # throws error if type is wrong
        instry(arg2, str)  # throws error if type is wrong
        def wrapper(func):
            return Node(func, arg1, arg2)
        return wrapper
    
    def extend(self, arg1, arg2=""):
        '''Decorator to convert function to root node
        Using:
        @Node.setup
        def func():
            pass
        
        or:
        @Node.setup([str]name, [str]desc)
        def func():
            pass

        after:
        @func.extend
        def subfunc():
            pass

        or:
        @func.extend([str]name, [str]desc)
        def subfunc():
            pass
        '''
        if callable(arg1):
            res = Node(arg1)
            self.insertNode(res)
            return res
        # other way, arg1 is name and arg2 is description
        instry(arg1, str)  # throws error if type is wrong
        instry(arg2, str)  # throws error if type is wrong

        def wrapper(func):
            res = Node(func, arg1, arg2)
            self.insertNode(res)
            return res
        return wrapper
    
    def expand(self, arg1, arg2=""):
        '''Decorator to convert function to root node
        Using:
        @Node.setup
        def func():
            pass
        
        or:
        @Node.setup([str]name, [str]desc)
        def func():
            pass

        after:
        @func.extend
        def subfunc():
            pass

        or:
        @func.extend([str]name, [str]desc)
        def subfunc():
            pass
        '''
        if callable(arg1):
            res = Node(arg1)
            self.insertNode(res)
            return None
        # other way, arg1 is name and arg2 is description
        instry(arg1, str)  # throws error if type is wrong
        instry(arg2, str)  # throws error if type is wrong

        def wrapper(func):
            res = Node(func, arg1, arg2)
            self.insertNode(res)
            return None
        return wrapper
