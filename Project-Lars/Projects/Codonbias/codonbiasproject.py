codon_map = {
    "TTT": "F",
    "TTC": "F",
    "TTA": "L",
    "TTG": "L",
    "TCT": "S",
    "TCC": "S",
    "TCA": "S",
    "TCG": "S",
    "TAT": "Y",
    "TAC": "Y",
    "TAA": "*",
    "TAG": "*",
    "TGT": "C",
    "TGC": "C",
    "TGA": "*",
    "TGG": "W",
    "CTT": "L",
    "CTC": "L",
    "CTA": "L",
    "CTG": "L",
    "CCT": "P",
    "CCC": "P",
    "CCA": "P",
    "CCG": "P",
    "CAT": "H",
    "CAC": "H",
    "CAA": "Q",
    "CAG": "Q",
    "CGT": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "ATT": "I",
    "ATC": "I",
    "ATA": "I",
    "ATG": "M",
    "ACT": "T",
    "ACC": "T",
    "ACA": "T",
    "ACG": "T",
    "AAT": "N",
    "AAC": "N",
    "AAA": "K",
    "AAG": "K",
    "AGT": "S",
    "AGC": "S",
    "AGA": "R",
    "AGG": "R",
    "GTT": "V",
    "GTC": "V",
    "GTA": "V",
    "GTG": "V",
    "GCT": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "GAT": "D",
    "GAC": "D",
    "GAA": "E",
    "GAG": "E",
    "GGT": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
}

#############################################################
# Write your functions definitions below.
# Do not write any other code here.
#############################################################

# only your function definitions...
File = "Project-Lars\codonbias\sample_orfs.txt"


def read_data(filename):

    with open(filename) as f:
        return [x for x in f.read().splitlines()]


def split_codons(orf):
    result = []
    for i in range(0, len(orf) - 2, 3):
        result.append(orf[i : i + 3])
    return result


def count_codons(orf):
    dict = {}
    for codon in codon_map.keys():
        dict[codon] = 0
    for i in split_codons(orf):
        if i in codon_map:
            dict[i] = dict[i] + 1
    return dict


def group_counts_by_amino_acid(dict):
    dick = {}
    for i in codon_map.values():
        dick[i] = {}  # dick[key] = value () #key = 1letter value = {}
    for codon in dict:  # codon = ["CTT", "ATA"] "CTT"
        dick[codon_map[codon]][codon] = dict[codon]  #
    return dick


# That means that in cases where the total count is zero, the function must return None
def normalize_counts(groupcounts):
    counts = {}
    if sum(groupcounts.values()) > 0:
        for i in groupcounts:
            counts[i] = groupcounts[i] / sum(groupcounts.values())
    else:
        return None
    return counts


def normalize_grouped_counts(dickcounts):
    dict = {}
    for acid in dickcounts:
        if sum(dickcounts[acid].values()) > 0:
            dict[acid] = normalize_counts(
                dickcounts[acid]
            )  # normalize_counts({'GCA': 0, 'GCC': 0, 'GCT': 0, 'GCG': 0})
    return dict


def codon_usage(orf):
    return normalize_grouped_counts(group_counts_by_amino_acid(count_codons(orf)))


# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...

# print(read_data(File))
# print(group_counts_by_amino_acid(count_codons("ATGTCATCATGA")))
print(codon_usage(read_data(File)[1]))

