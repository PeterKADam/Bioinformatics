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
def translate_codon(codon):
    if codon in codon_map:
        return codon_map[codon]
    else:
        return "?"


def split_codons(orf):
    result = []
    for i in range(0, len(orf), 3):
        result.append(orf[i : i + 3])
    return result


def translate_orf(seq):
    result = []  # Tom liste
    for codon in split_codons(
        seq
    ):  # Går igennem de forskellige værdier i listen fra split_codons
        result.append(
            translate_codon(codon)
        )  # Tilføjer den enkelte værdi der tilhører nøglen "Codon"
    return "".join(result)


#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...

print(translate_codon("ACG"))

print(split_codons("ATGGAGCTTANCAAATAG"))

print(translate_orf("ATGGAGCTTANCAAATAG"))
