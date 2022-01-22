#############################################################
# Write your functions definitions below.
# Do not write any other code here.
#############################################################

# only your function definitions...


def sequence_similarity(seq1, seq2):
    x = 0
    for i in range(len(seq1)):
        if seq1[i] == seq2[i]:
            x += 1
    return x / len(seq1)


def alignment_similarity(dna1, dna2):
    x = 0
    y = 0
    for i in range(len(dna1)):
        if dna1[i] == "-" and dna2[i] == "-":
            y += 1
        elif dna1[i] == dna2[i]:
            x += 1
    return x / (len(dna1) - y)


def read_data(RPATH):
    # RPATH = r"Project-Lars\Hivproject\unknown_type.txt"

    with open(RPATH) as f:
        return [x for x in f.read().splitlines()]


unknown_list = read_data(r"Project-Lars\Hivproject\unknown_type.txt")


def load_typed_sequences():
    return {
        "A": read_data(r"Project-Lars\Hivproject\subtypeA.txt"),
        "B": read_data(r"Project-Lars\Hivproject\subtypeB.txt"),
        "C": read_data(r"Project-Lars\Hivproject\subtypeC.txt"),
        "D": read_data(r"Project-Lars\Hivproject\subtypeD.txt"),
    }


typed_data = load_typed_sequences()


def get_similarities(unknownseq, typelist):
    list = []
    for i in typelist:
        list.append(alignment_similarity(unknownseq, i))
    return list


def get_max_similarities(seq, dic):
    highest = {}
    for typeset in dic:
        highest[typeset] = max(get_similarities(seq, dic[typeset]))
    return highest


def predict_subtype(seq, dic):
    var = get_max_similarities(seq, dic)
    return max(var, key=var.get)  # Returnerer den nøgle, hvorved maks værdi er


#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...


print(predict_subtype(unknown_list[0], typed_data))
# print(typed_data["A"])
