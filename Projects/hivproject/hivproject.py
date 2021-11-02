#############################################################
# Write your functions definitions below.
# Do not write any other code here.
#############################################################

# only your function definitions...


def read_data(hivtype):
    if hivtype == "unknown":
        RPATH = "Projects\hivproject\unknown_type.txt"
    else:
        RPATH = "Projects\hivproject\subtype{}.txt".format(hivtype)
    with open(RPATH) as f:
        return "".join([x for x in f.read().splitlines()])


def sequence_similarity(seq1, seq2):
    d = 0
    # range is retardproofed by user verification and is equal for both args
    for i in range(len(seq1)):
        if seq1[i] == seq2[i]:
            d += 1

    return d / len(seq1)


def alignment_similarity(seq1_gap, seq2_gap):
    gaps = 0
    d = 0
    for i in range(len(seq1_gap)):
        if seq1_gap[i] == "-" and seq2_gap[i] == "-":
            gaps += 1
            continue
        if seq1_gap[i] == seq2_gap[i]:
            d += 1

    return d / (len(seq1_gap) - gaps)


def load_typed_sequences():
    return {
        "A": read_data("A"),
        "B": read_data("B"),
        "C": read_data("C"),
        "D": read_data("D"),
    }


def get_similarities(unknownseq, db_type_seq_list):
    return [alignment_similarity(unknownseq, x) for x in db_type_seq_list]


#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...

# print(alignment_similarity("A-CT-A", "A-CTTA"))
print(get_similarities(read_data("unknown"), load_typed_sequences()))
