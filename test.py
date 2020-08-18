from PyEx.Events import delegate, Event, evented
from PyEx import Node

# 4 dummy functions
@Node.setup
def f1(evt=None):
    print("f1:", evt)

@f1.extend("lang")
def f2(evt=None):
    print("f2:", evt)

@f1.lang.extend("set")
def f3(evt=None):
    print("f3:", evt)


@f1.lang.set.extend
def f4(evt=None):
    print("f4:", evt)


@f1.lang.set.f4.extend
def f5(evt=None):
    print("f5:", evt)


print(f1)
print(f2)
print(f3)
print(f4)
print(f5)
