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
    dict = {}
    for each in range(len(pseq)):
        if pseq[each] not in dict:
            dict[pseq[each]] = 0
        dict[pseq[each]] += 1
    return dict


def mean_hydrophobicity(hscores):
    return sum(hscores) / len(hscores)


def running_mean(hscores, overlaps):
    return [
        sum(hscores[each : each + overlaps]) / overlaps
        for each in range(len(hscores) - overlaps + 1)
    ]


def find_hydrophobic(pseq, hscores):
    return [pseq[each] for each in range(len(pseq)) if hscores[each] > 0]


def mask_hydrophobic_aa(pseq, hscores):
    return "".join(
        pseq[each].lower() if hscores[each] > 0 else pseq[each]
        for each in range(len(pseq))
    )


def hydrophobic_subseqs(pseq, hscores):
    subseqlist = []
    subsublist = []
    for each in range(len(pseq)):
        if hscores[each] > 0:
            subsublist.append(pseq[each])
        elif hscores[each] <= 0 and len(subsublist) > 0:
            subseqlist.append("".join(subsublist))
            subsublist = []
    if len(subsublist) > 0:
        subseqlist.append("".join(subsublist))
    return subseqlist


def neighbor_hydrophobicity(pseq, hscores):
    dict = {}
    for each in range(len(pseq)):
        if pseq[each] not in dict:
            dict[pseq[each]] = [0, 0]
        if each < len(pseq) - 1:
            dict[pseq[each]][0] += hscores[each + 1]
            dict[pseq[each]][1] += 1
        if each > 0:
            dict[pseq[each]][0] += hscores[each - 1]
            dict[pseq[each]][1] += 1
    return {each: dict[each][0] / dict[each][1] for each in dict}


######################################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
######################################################################

# any other code that you delete before you submit your assignment ...

