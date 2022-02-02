######################################################################
# Write your functions definitions below.
# Do not write any other code here.
######################################################################

# only your function definitions...

# Problem 1
def longest_sequence(seq1, seq2):
    return [seq2, seq1][len(seq1) >= len(seq2)]


# Problem 2 #
def numbers_of_bases(seq):
    dict = {"A": 0, "T": 0, "G": 0, "C": 0}
    for i in range(len(seq)):
        dict[seq[i]] += 1
    return dict


# Problem 3 #
def numbers_of_triplets(seq):
    dict = {}
    for codon in range(0, len(seq) - 3 + 1):
        if seq[codon : codon + 3] not in dict:
            dict[seq[codon : codon + 3]] = 0
        dict[seq[codon : codon + 3]] += 1
    return dict


# Problem 4 #
def most_common_triplet(dict):
    return max(dict, key=dict.get)


# Problem 5 #
def column_sums(matrix):
    sumlist = []
    for y in range(len(matrix)):
        columnvalues = []
        for x in range(len(matrix)):
            columnvalues.append(matrix[x][y])
        sumlist.append(sum(columnvalues))
    return sumlist


# Problem 6 #


def mean_base_dist(seq, base):
    basepos = []
    for b in range(len(seq)):
        if seq[b] == base:
            basepos.append(b)

    distlist = []

    for each in range(len(basepos)):
        for every in range(len(basepos)):
            if every > each:
                # print(each, every)
                distlist.append(basepos[every] - basepos[each])

    if len(distlist) == 0:
        return None
    else:
        return sum(distlist) / len(distlist)


# problem 7 #
def find_differences(seq1, seq2):
    return [x for x in range(len(seq1)) if seq1[x] != seq2[x]]

