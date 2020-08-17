from PyEx.Events import delegate, Event, evented

# 4 dummy functions
def f1(evt=None):
    print("f1:", evt)
def f2(evt=None):
    print("f2:", evt)
def f3(evt=None):
    print("f3:", evt)
def f4(evt=None):
    print("f4:", evt)
def f5(evt=None):
    print("Function in delegate in called delegate:", evt)


actions = delegate() # infinite capacity

actions = delegate(1) # delegate can contain only 1 function

actions = delegate(0, f1, f2) # unlimited delegate wit 2 functions inside

actions2 = delegate(8) + f3 + f4  # limited delegate with 2 / 8 functions inside
actions2.add(f3, f2, f1) # one more way to add functions to 

print("actions:", actions)
print("actions2:", actions2)

print("Summation of delegates:")
print("actions + actions2 merging:", actions + actions2) # limit n + limit m = limit (n + m)
# merging method:
# actions.merge(actions2)
actions += actions2 # but its some faster

actions2.clear().add(f5) # clear and refill
actions.add(actions2) # put one delegate iside other


print(".invoke Method result:")
actions.invoke(2240)
print("call Method result:")
actions(2240)


