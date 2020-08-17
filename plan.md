# Wrappers:

## Node sructurized wrapper class
Some class to build method trees. Functions with sub-functions. Sub-functions with sub-sub-functions etc.
```python
z = Node(func1, "Description","Name1").insert(s_func1, "Description","Name2").insert(s_func1, "Description","Name3")
z["Name1.name.2"].insert(ss_func1, "Name4", "ThirdLayer")

z() # calls original. root function
z["Name1.Name2"]() # call child function
z[("Name1", "Name2")]() # call child function (alternate for automation)
z.Name1.Name2.Name4() # by __gettattr__ call child functions comfortable

@z.Name3.extend
def functa(mytrash=None, **kwargs):
    just()
    do()
    it()
    return mytrash

@z.Name3.extend("Overnaming", "descriptions and docstrings will be set automatically")
def functa(mytrash=None, **kwargs):
    just()
    do()
    it()
    return mytrash

#after it:
z.Name3.functa() #It`s works!!!

z.case_sensitive(False) # case sensitivity change to node and all nodes inside recursively

Events.
z.subscribe(acting=handler)
```