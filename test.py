from PyEx.Events import delegate, Event, evented
from PyEx import Node
from PyEx.Etime import Etime
from PyEx.Experimental import cmdl
from PyEx.Functors import functor



x = cmdl("@chat.send-to.all: 92% $var >>> $ret #comment")


@functor.create("test", "Some description", rest=0)
def test(func, i=0):
    func.res += 1
    return i, func.rest


print(test.callon(2))
























#input("Enter")
