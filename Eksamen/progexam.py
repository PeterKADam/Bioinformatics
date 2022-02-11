######################################################################
# Write your functions definitions below.
# Do not write any other code here.
######################################################################

# only your function definitions...
def seq_length(pseq):
    return len(pseq)


def same_length(pseq, hscores):
    return len(pseq) == len(hscores)


def aminoacid_counts(pseq):
    return {k: pseq.count(k) for k in pseq}


def mean_hydrophobicity(hscores):
    return sum(hscores) / len(hscores)


def running_mean(hscores, overlaps):
    return [
        sum(hscores[each : each + overlaps]) / overlaps
        for each in range(len(hscores) - overlaps + 1)
    ]


def find_hydrophobic(pseq, hscores):
    return [a for a, b in zip(pseq, hscores) if b > 0]


def mask_hydrophobic_aa(pseq, hscores):
    return "".join([a.lower() if b > 0 else a for a, b in zip(pseq, hscores)])


def hydrophobic_subseqs(pseq, hscores):
    subseqlist = []
    subsublist = []
    for a, b in zip(pseq, hscores):
        if b > 0:
            subsublist.append(a)
        elif b <= 0 and len(subsublist) > 0:
            subseqlist.append("".join(subsublist))
            subsublist = []
    if len(subsublist) > 0:
        subseqlist.append("".join(subsublist))
    return subseqlist


def neighbor_hydrophobicity(pseq, hscores):
    dict = {}
    for i, (a, b) in enumerate(zip(pseq, hscores)):
        if a not in dict:
            dict[a] = [0, 0]
        if i < len(pseq) - 1:
            dict[a][0] += hscores[i + 1]
            dict[a][1] += 1
        if i > 0:
            dict[a][0] += hscores[i - 1]
            dict[a][1] += 1
    return {each: dict[each][0] / dict[each][1] for each in dict}


######################################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
######################################################################

# any other code that you delete before you submit your assignment ...

