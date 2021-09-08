def is_base_pair(x,y):
    if (x =='A' and y == 'T') or (x =='T' and y == 'A'):
        return True
    if (x =='C' and y == 'G') or (x =='G' and y == 'C'):
        return True
    else: return False
print(is_base_pair("T","A"))
