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

if __name__ != "__main__":
    RPATH = "sample_orfs.txt"
else:
    RPATH = "Projects\codonbiasproject\sample_orfs.txt"


def read_data(filename: str = RPATH):

    with open(filename) as f:
        return [x for x in f.read().splitlines()]


def split_codons(orf):
    return [orf[x : x + 3] for x in range(0, len(orf) - 2, 3)]


def count_codons(orf: str):

    d = {x: 0 for x in codon_map.keys()}

    for codon in split_codons(orf):
        if codon in codon_map:
            d[codon] = d[codon] + 1
    return d


def group_counts_by_amino_acid(counts: dict):

    d = {x: {} for x in codon_map.values()}

    for codon in counts.keys():
        d[codon_map[codon]][codon] = counts[codon]
    return d


def normalize_counts(grouped_counts: dict):

    if sum(grouped_counts.values()) > 0:
        return {
            codon: grouped_counts[codon] / sum(grouped_counts.values())
            for codon in grouped_counts
        }


def normalize_grouped_counts(grouped_counts: dict):

    d = {}

    for acid in grouped_counts.keys():
        if sum(grouped_counts[acid].values()) > 0:
            d[acid] = normalize_counts(grouped_counts[acid])

    return d


def codon_usage(orf: str):
    return normalize_grouped_counts(group_counts_by_amino_acid(count_codons(orf)))


#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...

# print(count_codons("ATGTCATCATGA"))

