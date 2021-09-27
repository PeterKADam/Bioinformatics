def is_bp(x,y):
    return any(e in [x+y,y+x] for e in ["AT","GC"])
print(is_bp("G","C"))
    #for each in [x+y,y+x]:
    #    if each in ["AT","GC"]: return True
    #return False
    