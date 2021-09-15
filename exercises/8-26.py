def is_nucleotide_symbol(x):
    if (x.upper() in 'ATCG') and len(x)==1:
        return True
    else: return False

print(is_nucleotide_symbol("A"))
