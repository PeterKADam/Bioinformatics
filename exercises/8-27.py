def is_bp(x,y):
    for each in [x+y,y+x]:
        if each in ["AT","GC"]: return True
        else: return False
print(is_bp("A","T"))