#############################################################
# Write your functions definitions below.
# Do not write any other code here.
#############################################################

# only your function definitions...


def count_bases(seq):
    count = {"C": 0, "G": 0, "T": 0, "A": 0}
    for base in seq:
        count[base] += 1
    return count


def melting_temp(seq):
    i = count_bases(seq)
    if len(seq) < 14:
        return (i["A"] + i["T"]) * 2 + (i["C"] + i["G"]) * 4
    return 64.9 + 41 * (i["G"] + i["C"] - 16.4) / (len(seq))


def reverse_complement(seq):
    reversedseq = ""
    for base in range(len(seq) - 1, -1, -1):
        if seq[base] == "A":
            reversedseq += "T"
        if seq[base] == "T":
            reversedseq += "A"
        if seq[base] == "G":
            reversedseq += "C"
        if seq[base] == "C":
            reversedseq += "G"
    return reversedseq


def has_hairpin(seq, int):
    looplen = 4
    for i in range(len(seq) - int + 1):
        subs = seq[i : i + int]
        right = seq[i + int :]
        revcl = reverse_complement(subs)
        if revcl in right[looplen:]:
            return True
        return False


#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...

print(has_hairpin("ATATACCCCTATAT", 4))
