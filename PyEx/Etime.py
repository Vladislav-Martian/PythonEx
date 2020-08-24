from PyEx.Errors import Error, AccessError, ParsingError, TypingError, instry
import time
#===============================================
__all__ = ["Etime"]
#===============================================
calendar = {
    "ms": 1,
    "s": 1000,
    "m": 1000 * 60,
    "h": 1000 * 60 * 60,
    "d": 1000 * 60 * 60 * 24,
    "w": 1000 * 60 * 60 * 24 * 6,
    "mn": 1000 * 60 * 60 * 24 * 6 * 5,
    "y": 1000 * 60 * 60 * 24 * 6 * 5 * 12,
    "mr": 1000 * 60 * 60 * 24 * 6 * 5 * 12 * 10000,
    "er": 1000 * 60 * 60 * 24 * 6 * 5 * 12 * 10000 * 100,
    "ep": 1000 * 60 * 60 * 24 * 6 * 5 * 12 * 10000 * 100 * 1000,
    "eo": 1000 * 60 * 60 * 24 * 6 * 5 * 12 * 10000 * 100 * 1000 * 1000,
}
months = ["March", "April", "May", "June", "July", "August", "September", "October", "November", "december", "January", "Fabruary"]


class Etime(object):
    NowIniter = None
    NowStart = None

    @staticmethod
    def start(date):
        Etime.NowIniter = int(time.time()) * 1000
        Etime.NowStart = date
        return Etime
    '''Class to realize perfect calendar
    1 second = 100 ms
    1 minute = 60 s
    1 hour = 60 m
    1 day = 24 h
    1 week = 6 d
    1 month = 30 d (5 weeks)
    1 year = 12 mn (360 d, 60 weeks)
    Static:
        None

    Constructor:
        >> Etime(ms):
            [int] ms - timestamp in milliseconds

    Attributes:
        

    In-Services:
        static [str] __counter__ - used to automatically generate names to unnamed functor or lambda nodes
    '''
    def __init__(self, ms=0, **kwargs):
        instry(ms, int)
        self.ms = ms
        self.s = 0
        self.m = 0
        self.h = 0
        self.d = 0
        self.mn = 0
        self.y = 0
        self.mr = 0
        self.er = 0
        self.ep = 0
        self.eo = 0
        self.shift = 0
        self.add(**kwargs)
        self.normalize()

    def add(self, **kwargs):
        for key in kwargs:
            if key in calendar:
                setattr(self, key, getattr(self, key) + kwargs[key])
        return self.normalize()
    
    def stamp(self):
        return self.ms + self.s * calendar["s"] + self.m * calendar["m"] + self.h * calendar["h"] + self.d * calendar["d"] + self.mn * calendar["mn"] + self.y * calendar["y"] + self.mr * calendar["mr"] + self.er * calendar["er"] + self.ep * calendar["ep"] + self.eo * calendar["eo"]

    def normalize(self):
        buf = self.stamp()
         
        self.eo = buf // calendar["eo"]
        buf = buf - self.eo * calendar["eo"]
         
        self.ep = buf // calendar["ep"]
        buf = buf - self.ep * calendar["ep"]
         
        self.er = buf // calendar["er"]
        buf = buf - self.er * calendar["er"]
         
        self.mr = buf // calendar["mr"]
        buf = buf - self.mr * calendar["mr"]
        #=============
         
        self.y = buf // calendar["y"]
        buf = buf - self.y * calendar["y"]
         
        self.mn = buf // calendar["mn"]
        buf = buf - self.mn * calendar["mn"]
         
        self.d = buf // calendar["d"]
        buf = buf - self.d * calendar["d"]
        #================
         
        self.h = buf // calendar["h"]
        buf = buf - self.h * calendar["h"]
         
        self.m = buf // calendar["m"]
        buf = buf - self.m * calendar["m"]
         
        self.s = buf // calendar["s"]
        buf = buf - self.s * calendar["s"]
         
        self.ms = buf
        return self

    def monthname(self):
        return months[self.normalize().mn]
    
    def weekday(self):
        n = (self.d + 1) % 6
        if n == 1:
            return "Monday"
        elif n == 2:
            return "Tuesday"
        elif n == 3:
            return "Wednesday"
        elif n == 4:
            return "Thursday"
        elif n == 5:
            return "Friday"
        elif n == 0:
            return "Saturday"

    def __hash__(self):
        return self.stamp()

    def setShift(self, sh):
        self.shift = (abs(sh) % 12) * (1 if sh >= 0 else -1)
        return self
    
    def __repr__(self):
        self.normalize()
        return f"Date[{self.eo}. {self.ep}. {self.er}. {self.mr}. / {self.y + 1}. {self.mn + 1}. {self.d + 1}. W{self.getweek()} ({self.weekday()}) / {self.h}:{self.m}:{self.s}.{self.ms} S:{'+' if self.shift >= 0 else '-'}{abs(self.shift)}]"
    
    def getweek(self):
        return (self.d // 6) + 1
    
    #===============
    def __sub__(self, other):
        instry(other, Etime)
        return Etime(self.stamp() - other.stamp())
    
    def __add__(self, other):
        instry(other, Etime)
        return Etime(self.stamp() + other.stamp())
    
    #================
    @staticmethod
    def now():
        if Etime.NowIniter == None:
            Etime.start(0)
        return Etime(int(time.time() * 1000) - Etime.NowIniter + Etime.NowStart)