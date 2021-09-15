def is_bp(x,y):
    i=["AT","GC"]
    return x+y in i or y+x in i
print(is_bp("C","G"))
    #for each in [x+y,y+x]:
    #    if each in ["AT","GC"]: return True
    #return False
    