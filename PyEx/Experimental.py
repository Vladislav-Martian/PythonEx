from PyEx.Events import delegate, Event, evented
from PyEx.Errors import Error, AccessError, ParsingError, instry
from os import system, name as osname
from colorama import Fore, init
init(convert=True)
#===============================================
__all__ = [
    "cmdl"
]
#===============================================
class NotCallableError(Error):
    pass

def intable(string):
    try:
        int(string)
    except:
        return False
    else:
        return True

def floatable(string):
    try:
        float(string)
    except:
        return False
    else:
        return True
#===============================================
'''
Command examles:
/starengine.getgenerator: "stellaris" >=> $gen
/starengine.generate.by: $gen "Neosol" #r #t >=> $system
0|===2====|1|===2==|1|23_|4=|_|==4===|_|5|_|==6==|
0 - command igniter [/><!#?@]{1-3}
2 - call stack. Aress ffor some function in call tree.
1 - separator
3 - call stack ender signal
4 - argument to call
5 - type of return (mb no return) >>> - strong return (anyway), >=> return if command has returned value, >-> week return
6 - list of variables to return

Values:
Strings - "Text text text"
VariableAcessors - $var
Numbers:
    120270  - int
    3.14    - float
    34.5%   - float
    12f     - float
    34.5    - int
flags - #t
bools - true/false
nothing - null, none
tag - @tagtext
'''

class tag(object):
    def __init__(self, name):
        name = str(name).lower()
        if name.startswith('@'):
            name = name[1:]
        self.name = name
    
    def __repr__(self):
        return f"@({self.name})"
    
    def __str__(self):
        return repr(self)
    
    def __eq__(self, other):
        if not isinstance(other, tag):
            return False
        return self.name == other.name
    
    def __ne__(self, other):
        if not isinstance(other, tag):
            return False
        return self.name != other.name
    
    def __hash__(self):
        return hash(repr(self))

class Handler(object):
    pass

class CommandSession(object):
    _id_ = 0
    def __init__(self, handler):
        instry(handler, Handler)
        self.handler = handler
        self.variables = {}
        self._id = CommandSession._id_
        self.errflow = []
        self.mesflow = []
        self.meslimit = 20
        CommandSession._id_ += 1
    
    @property
    def id(self):
        return self._id
    
    def __call__(self, cmd):
        if isinstance(cmd, str):
            cmd = cmdl(cmd)
        cmd.session = self
        for arg in cmd.args:
            if isinstance(arg, VarAccessor):
                arg.link(self.variables)
        ret = None
        try:
            ret = self.handler(cmd)
        except Exception as err:
            self.errflow.append(err)
            return self
        if cmd.rettype == 1:
            for retl in cmd.retlist:
                self.variables[retl] = ret
        elif cmd.rettype == 2:
            for retl in cmd.retlist:
                if ret != None:
                    self.variables[retl] = ret
        elif cmd.rettype == 2:
            for retl in cmd.retlist:
                if ret != None and self.variables[retl] == None:
                    self.variables[retl] = ret
        return self
    
    def consoleClear(self):
        if osname == 'nt':
            _ = system('cls')
        else:
            _ = system('clear')
    
    def consoleUpdate(self):
        self.consoleClear()
    
    def dialog(self):
        while True:
            pass


class VarAccessor(object):
    def __init__(self, name):
        self.name = str(name)
        self.space = None
    
    def __repr__(self):
        return f"{self.name}"
    
    def link(self, dic):
        instry(dic, dict)
        self.space = dic
        if not self.name in self.space:
            self.space[self.name] = None
        return self
    
    def unlink(self):
        if not self.isLinked():
            raise AccessError(
                "Variable accessor are not linked to variable space dictionary")
        del self.space[self.name]
        self.space = None
        return self
    
    def isLinked(self):
        return self.space != None
    
    @property
    def port(self):
        if not self.isLinked():
            raise AccessError("Variable accessor are not linked to variable space dictionary")
        return self.space[self.name]
    
    @port.setter
    def port(self, val):
        if not self.isLinked():
            raise AccessError(
                "Variable accessor are not linked to variable space dictionary")
        self.space[self.name] = val
    
    @port.deleter
    def port(self):
        if not self.isLinked():
            raise AccessError(
                "Variable accessor are not linked to variable space dictionary")
        del self.space[self.name]


class cmdl(object):
    actors = "/><!#?@"
    actorsmaxlen = 3
    namechar = "-=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    whitespace = " ,\u0009\u00A0\u2008\u2009\u2000\u2001\u2002\u2003"
    quotes = "\'\""
    def __init__(self, cmd=None):
        self.actor = "/"
        self.cstack = []
        self.rettype = 0 # no return by default
        self.retlist = []
        self.flags = ""
        self.args = []
        self.session = None
        if isinstance(cmd, str):
            self.parse(cmd)
    
    def parse(self, cmd):
        actor = cmd[0]
        if not actor in cmdl.actors: # errors
            raise ParsingError(f"Unposible to act from '{actor}' because it is not in available actors '{cmdl.actors}")
        actor2 = ""
        for x in range(cmdl.actorsmaxlen):
            if cmd[x] == actor:
                actor2 += cmd[x]
            else:
                break
        self.actor = actor2
        if cmd[len(actor2)]== actor:
            raise ParsingError(f"Actor too long. Max length is {cmdl.actorsmaxlen}")
        # cmd actor got
        cmd = cmd[len(actor2):] # cut part of command without actor
        # get return configuration from command
        detected = 0
        i = -1
        last = len(cmd) - 1
        makevar = False
        timed = ""
        returnings = []
        for char in cmd:
            i += 1
            if detected == 0 and char == ">":
                detected = True
                continue
            elif detected == 1:
                if char == ">":
                    self.rettype = 1
                    detected = 2
                    continue
                elif char == "=":
                    self.rettype = 2
                    detected = 2
                    continue
                elif char == "-":
                    self.rettype = 3
                    detected = 2
                    continue
                else:
                    raise ParsingError(f"Unknown return type >{char}>")
            elif detected == 2:
                if char == ">":
                    detected = 3
                    continue
                else:
                    raise ParsingError(f"Unexpected character [{char}]")
            elif detected == 3:
                if not makevar and char == "$":
                    makevar = True
                    timed = ""
                    continue
                elif ((not makevar) and char in "\n.#") or i == last:
                    if makevar and char in cmdl.namechar:
                        timed += char
                    if len(timed) > 0:
                        returnings.append(f"${timed}")
                    self.retlist = returnings
                    break
                elif makevar and char in cmdl.namechar:
                    timed += char
                    continue
                elif makevar and char in cmdl.whitespace:
                    makevar = False
                    if len(timed) > 0:
                        returnings.append(f"${timed}")
                        timed = ""
                    continue
                elif not makevar and char in cmdl.whitespace:
                    continue
                else:
                    raise ParsingError(f"Unexpected character[{char}]")
            else:
                self.rettype = 0
                self.retlist.clear()
        #====================
        if self.rettype != 0:
            cmd = cmd[:cmd.find(f">{'>' if self.rettype == 1 else '=' if self.rettype == 2 else '-'}>")]
        # return config done!
        tms = ""
        stack = []
        leng = 0
        initor = True
        for char in cmd:
            leng += 1
            if initor and char in cmdl.whitespace:
                continue
            elif char in cmdl.namechar:
                initor = False
                tms += char
                continue
            elif char == ".":
                initor = False
                if len(tms) > 0:
                    stack.append(tms)
                    tms = ""
                continue
            elif char == ':':
                stack.append(tms)
                break
            else:
                raise ParsingError(f"Unexpected character [{char}]")
        self.cstack = stack
        cmd = cmd[leng:]
        # parse argument phase 1
        args = []
        tms = ""
        state = "main"
        i = -1
        last = len(cmd) - 1
        flags = ""
        for char in cmd:
            i += 1
            if state == "main" and char in cmdl.whitespace and len(tms) <= 0:
                continue
            elif state == "main" and char == '#':
                state = "flag"
                continue
            elif state == "flag" and char in cmdl.whitespace:
                state = "main"
                continue
            elif state == "flag" and char in '.\n#':
                break
            elif state == "flag":
                if not char in flags:
                    flags += char
                continue
            elif state == "main" and char in cmdl.quotes:
                state = "string"
                tms += "|"
                continue
            elif state == "string" and char in cmdl.quotes:
                state = "main"
                tms += "|"
                continue
            elif state == "string":
                tms += char
                continue
            elif state == "main" and char in cmdl.whitespace and len(tms) > 0:
                args.append(tms)
                tms = ""
                continue
            elif state == "main" and not char in cmdl.whitespace:
                tms += char
                continue
            elif state == "main" and i == last:
                break
            else:
                raise ParsingError(f"Unexpected character [{char}]")
        if len(tms) > 0:
            args.append(tms)
        self.args = cmdl.argumentparser(args)
        self.flags = "".join(sorted(flags))
        return self
    
    @staticmethod
    def argumentparser(args):
        i = -1
        for arg in args:
            i += 1
            #===========
            if arg.startswith('|') and arg.endswith('|'):
                args[i] = (arg[1:-1]).encode().decode("unicode_escape")
            elif arg.startswith('@'):
                args[i] = tag(arg[1:])
            elif arg.startswith('$'):
                args[i] = VarAccessor(arg)
            elif arg.endswith('i') and intable(arg[:-1]):
                args[i] = int(arg[:-1])
            elif arg.endswith('f') and floatable(arg[:-1]):
                args[i] = float(arg[:-1])
            elif arg.endswith('%') and floatable(arg[:-1]):
                args[i] = float(arg[:-1]) / 100
            elif floatable(arg):
                args[i] = float(arg)
            elif intable(arg):
                args[i] = int(arg)
            elif arg.lower() == "null" or arg.lower() == "none":
                args[i] = None
            elif arg.lower() == "true":
                args[i] = True
            elif arg.lower() == "false":
                args[i] = False
            else:
                args[i] = arg.encode().decode("unicode_escape")
        return args

    def __str__(self):
        res = self.actor
        res += '.'.join(self.cstack) + ": "
        if len(self.args) > 0:
            for arg in self.args:
                res += repr(arg) + " "
        if len(self.flags) > 0:
            res += f'#{self.flags} '
        if self.rettype != 0:
            res += f">{'>' if self.rettype == 1 else '=' if self.rettype == 2 else '-'}> "
            res += ' '.join(self.retlist)
        return res + '.'
    
    def __repr__(self):
        res = self.actor
        res += '.'.join(self.cstack) + ": "
        if len(self.args) > 0:
            for arg in self.args:
                if arg == None:
                    res += "null "
                    continue
                elif isinstance(arg, bool):
                    res += repr(arg).lower()
                    continue
                res += repr(arg) + " "
        if len(self.flags) > 0:
            res += f'#{self.flags} '
        if self.rettype != 0:
            res += f">{'>' if self.rettype == 1 else '=' if self.rettype == 2 else '-'}> "
            res += ' '.join(self.retlist)
        return res + '.'
    
    def colored(self):
        res = Fore.RED + self.actor + Fore.RESET
        lim = len(self.cstack) - 1
        i, j = -1, -1
        for call in self.cstack:
            i += 1
            j += 1
            color = Fore.LIGHTGREEN_EX if i == lim else Fore.YELLOW if  j % 2 == 0 else Fore.CYAN
            res += color + call + Fore.RESET
            if i != lim:
                res += Fore.RED + '.' + Fore.RESET
        res += ' '
        if len(self.args) > 0:
            for arg in self.args:
                if isinstance(arg, str):
                    res += Fore.WHITE + repr(arg) + Fore.RESET
                elif isinstance(arg, (int, float)):
                    res += Fore.MAGENTA + repr(arg) + Fore.RESET
                elif isinstance(arg, VarAccessor):
                    res += Fore.CYAN + repr(arg) + Fore.RESET
                elif isinstance(arg, tag):
                    res += Fore.LIGHTYELLOW_EX + repr(arg) + Fore.RESET
                elif isinstance(arg, bool):
                    res += Fore.RED + repr(arg).lower() + Fore.RED
                elif arg == None:
                    res += Fore.BLUE + "null" + Fore.RESET
                res += ' '
        if len(self.flags) > 0:
            res += f'{Fore.CYAN}#{self.flags}{Fore.RESET} '
        if self.rettype != 0:
            res += f"{Fore.RED}>{'>' if self.rettype == 1 else '=' if self.rettype == 2 else '-'}>{Fore.RESET} "
            i = -1
            lim = len(self.retlist) - 1
            for ret in self.retlist:
                i += 1
                res += Fore.CYAN + ret + Fore.RESET
                if i != lim:
                    res += " "
        return res + Fore.RED + '.' + Fore.RESET







#===============================================

