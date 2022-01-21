######################################################################
# Write your functions definitions below.
# Do not write any other code here.
######################################################################

# only your function definitions...
# Problem 1#
from enum import unique


def nr_rows_in_matrix(list):
    return len(list)


# Problem 2#
def count_stuff(iterable):
    dict = {}
    for i in range(len(iterable)):
        if iterable[i] not in dict:
            dict[iterable[i]] = 0
        dict[iterable[i]] += 1
    return dict


# Problem 3#
def invert_dictionary(dict):
    dick = {}
    for i in dict:
        dick[dict[i]] = i
    return dick


# Problem 4 #
def count_upper_case_bases(seq):
    count = 0
    for base in seq:
        if base in ["A", "C", "G", "T"]:
            count += 1
    return count


# Problem 5 #
def every_second_base(seq):
    list = []
    for base in range(0, len(seq), 2):
        list.append(seq[base])
    return list


# Problem 6 #
def splice_upper_case(seq):
    uppercase = ""
    for base in seq:
        if base in ["A", "C", "G", "T"]:
            uppercase += base
    return uppercase


# Problem 7 #
def kmer_locations(sdna, ldna):
    returnlist = []

    for i in range(len(ldna) - len(sdna) + 1):
        if sdna == ldna[i : i + len(sdna)]:
            returnlist.append(i)
    return returnlist


# Problem 8 #
def kmers_overlap(kmer1, kmer2, seq):

    if kmer1 in seq and kmer2 in seq:

        kmer1loc = kmer_locations(kmer1, seq)
        kmer2loc = kmer_locations(kmer2, seq)

        for each in kmer1loc:
            for every in kmer2loc:
                if abs(each - every) < len(kmer1):
                    return True

        return False
    else:
        return False


# Problem 9 #
def unique_kmers(seq, int):
    list = []
    for codon in range(0, len(seq) - int + 1):
        if seq[codon : codon + int] not in list:
            list.append(seq[codon : codon + int])
    return list


# Problem 10 #
def nr_unique_kmers_shared(seq1, seq2, int):

    nr = 0

    seq1kmers = unique_kmers(seq1, int)
    seq2kmers = unique_kmers(seq2, int)

    for kmer in seq1kmers:
        if kmer in seq2kmers:
            nr += 1
    return nr


# Problem 11 #
def kmer_sharing_matrix(seqlist, int):
    matrix = []
    for x in range(len(seqlist)):
        matrix.append([])
        for y in range(len(seqlist)):
            matrix[x].append(nr_unique_kmers_shared(seqlist[x], seqlist[y], int))
    return matrix

######################################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
######################################################################

# any other code that you delete before you submit your assignment ...
#
# print(kmers_overlap("TTAA", "AATT", "CCCCTTAATTCCCC"))
